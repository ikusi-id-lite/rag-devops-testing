import os
from dotenv import load_dotenv
from fastapi import FastAPI
import asyncio
from agents import Runner, handoff
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
import pandas as pd

from ai_agents import (AppContext,
                       create_triage_agent,
                       create_sql_statement_agent,
                       create_business_knowledge_agent,
                       create_sql_execute_agent,
                       create_products_agent,
                       create_previous_context_agent,
                       create_sql_execute_handoff,
                       create_presentation_agent,
                       create_out_of_context_agent,
                       create_presentation_agent_handoff,
                       create_knowledge_base_agent_handoff,
                       create_sql_statement_agent_handoff,
                       create_previous_context_agent_handoff,
                       create_out_of_context_agent_handoff
                       )

from agents.mcp import MCPServerSse

from agents import Runner

REDIS_URL = os.getenv("REDIS_URL")
#SESSION_ID = "rag:user:{ID_USUARIO}:conversation:{ID_CONVERSACION}:history"
#SESSION_ID = "rag:user:1:conversation:1:history"
MAX_CONTEXT_SIZE = 3
LOGGED_USER_ID = "1"

load_dotenv()

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def add_context(r: redis.Redis, key: str, obj_data: dict):
    """
    Añade un objeto a la lista y recorta automáticamente al tamaño máximo.
    Se usa un pipeline para ejecutar ambos comandos atómicamente.
    """

    json_string = json.dumps(obj_data)
    pipe = r.pipeline()
    pipe.lpush(key, json_string)
    pipe.ltrim(key, 0, MAX_CONTEXT_SIZE - 1)
    pipe.execute()
    print(f"Objeto añadido y lista recortada a {MAX_CONTEXT_SIZE} elementos.")

async def main(user_query: str = None, logged_user_rol: str = None):

  try:
      """ r = redis.Redis(host='localhost', port=6379, db=0) """
      r = redis.Redis(host=REDIS_URL, port=6379, db=0)
      r.ping()
      print("Conexión a Redis exitosa.")
  except redis.exceptions.ConnectionError as e:
      print(f"Error de conexión a Redis: {e}")
      print("Asegúrate de que tu servidor Redis esté iniciado.")
      exit()

  if logged_user_rol == "gerente_proyectos":
      SESSION_ID = "rag:user:1:conversation:1:history"
  else:
      SESSION_ID = "rag:user:2:conversation:1:history"

  previous_context = f"{r.lrange(SESSION_ID, 0, -1)}"

  print("----- CONTEXTO PREVIO RECUPERADO DE REDIS -----")
  print(previous_context)
  print(type(previous_context))
  print("------------------------------------------------")

  app_context = AppContext(user_query=user_query, previous_context=previous_context, logged_user_rol=logged_user_rol)

  workspace_id = "2-workspace"

    # http://mcp-server:8000/sse
    #local
    # http://127.0.0.1:8000/sse

  mcp_server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/sse")
  async with MCPServerSse(
    name="SSE Python Server",
    params={
        "url": mcp_server_url,
        "headers": {"X-Workspace": workspace_id},
        "timeout": 20,
    },
    cache_tools_list=True,
  ) as server:

      products_agent = create_products_agent(
        app_context=app_context,
        mcp_servers=[server]
      )

      presentation_agent = create_presentation_agent(
        app_context=app_context,
      )

      handoff_presentation_obj = create_presentation_agent_handoff(presentation_agent)

      execute_sql_agent = create_sql_execute_agent(
        app_context=app_context,
        mcp_servers=[server],
        handoffs=[handoff_presentation_obj]
      )

      handoff_execute_obj = create_sql_execute_handoff(execute_sql_agent)

      sql_agent = create_sql_statement_agent(
        app_context=app_context,
        handoffs=[handoff_execute_obj],
        mcp_servers=[server]
      )

      business_knowledge_agent = create_business_knowledge_agent(
        app_context=app_context,
        mcp_servers=[server]
      )

      business_knowledge_agent_handoff = create_knowledge_base_agent_handoff(business_knowledge_agent)

      sql_statement_agent_handoff = create_sql_statement_agent_handoff(sql_agent)

      answer_by_context_agent = create_previous_context_agent(app_context)

      answer_by_context_agent_handoff = create_previous_context_agent_handoff(answer_by_context_agent)

      out_of_context_agent = create_out_of_context_agent(app_context)

      out_of_context_agent_handoff = create_out_of_context_agent_handoff(out_of_context_agent)

      prodcuts_agent_handoff = handoff(
        agent=products_agent,
        tool_name_override="agent_to_delegate_products_answer",
        tool_description_override="Herramienta personalizada para delegar la respuesta basada en productos empresariales actuales",
      )

      router_search_agent = create_triage_agent(
        app_context=app_context,
        handoffs=[answer_by_context_agent_handoff, sql_statement_agent_handoff, business_knowledge_agent_handoff, prodcuts_agent_handoff, out_of_context_agent_handoff]
      )

      result = await Runner.run(router_search_agent, user_query, context=app_context)
      print(result.final_output)
      print(type(result.final_output))
      print(result)

      times = app_context.timestamps
      debugging_info = app_context.debugging_info
      print("----- TIMESTAMPS RECOPILADOS -----")
      print(times)
      print("----- DEBUGGING INFO RECOPILADA -----")
      print(debugging_info)
      print("----------------------------------")

      print(result.last_agent.name)
      print(type(result.last_agent))

      finish_agents_allowed = [
        "Agente de respuesta por contexto",
        "Agente de Presentación de Resultados",
        "Agente de Búsqueda en la Base de Conocimiento",
        "Agente de respuesta fuera de contexto",
        "Agente experto en productos empresariales"
      ]

      if result.last_agent.name not in finish_agents_allowed:
        print("La respuesta no ha sido generada por un agente esperado.")
        diccionario_python = {
          "error": "La respuesta no ha sido generada por un agente esperado.",
          "last_agent": result.last_agent.name,
          "expected_agents": finish_agents_allowed
        }
      else:
        print(f"La respuesta ha sido generada por el agente {result.last_agent.name}.")
        diccionario_python = result.final_output.model_dump()
        add_context(r, SESSION_ID, diccionario_python)

      print("----- DURACIONES ENTRE TIMESTAMPS -----")
      print(debugging_info)
      print("---------------------------------------")

      diff_between_timestamps = [times[i] - times[i-1] for i in range(1, len(times))]

      print("----- DURACIONES ENTRE TIMESTAMPS 2 -----")
      print(diff_between_timestamps)
      print("---------------------------------------")

      try:
        df_debug = pd.DataFrame(diff_between_timestamps)

        csv_debug_name = "debuggin_info.csv"

        df_debug.to_csv(
          csv_debug_name,
          index=True,
          encoding='utf-8'
        )

        print(f"Archivo CSV de tiempos creado exitosamente como '{csv_debug_name}'")
      except Exception as e:
        print(f"Error al crear el archivo CSV: {e}")

      return diccionario_python


from pydantic import BaseModel

class QueryRequest(BaseModel):
    user_query: str
    user_rol: str

@app.post("/api/ask")
async def ask_agent(request: QueryRequest):
    """
    Endpoint para enviar una consulta al sistema de agentes.
    """
    print("rol del usuario:", request.user_rol)
    try:
        result = await main(request.user_query, request.user_rol)
        return result
    except Exception as e:
        error_message= f"Error al procesar la consulta: {e}"
        return {"error": error_message}

@app.get("/times_last_report")
async def get_times_last_report():
    """
    Endpoint para obtener el último informe de tiempos.
    """
    try:
      df = pd.read_csv("debuggin_info.csv")
      result = df.to_dict(orient="records")
      return {
        "data": {
          "times_report": result
        }
      }
    except Exception as e:
        error_message= f"Error al obtener el informe de tiempos: {e}"
        return {"error": error_message}

@app.get("/greeting")
async def greeting():
    """
    Endpoint para enviar un saludo.
    """
    return {"message": f"Hola, has enviado la consulta"}

@app.delete("/cache/flushall")
async def flush_redis_database():
  try:
    r = redis.Redis(host=REDIS_URL, port=6379, db=0)
    r.ping()
    r.flushall()
    return {"message": "Base de datos Redis limpiada exitosamente."}
  except redis.exceptions.ConnectionError as e:
    print(f"Error de conexión a Redis: {e}")
    print("Asegúrate de que tu servidor Redis esté iniciado.")
    return {"error": "No se pudo conectar a Redis. Asegúrate de que el servidor esté iniciado."}


@app.get("/user/{user_id}/session/{session_id}")
def get_session(user_id: int, session_id: int):
    try:
      r = redis.Redis(host=REDIS_URL, port=6379, db=0)
      r.ping()
      print("Conexión a Redis exitosa.")
    except redis.exceptions.ConnectionError as e:
      print(f"Error de conexión a Redis: {e}")
      print("Asegúrate de que tu servidor Redis esté iniciado.")
      exit()

    SESSION_ID = f"rag:user:{user_id}:conversation:1:history"

    previous_context = f"{r.lrange(SESSION_ID, 0, -1)}"

    if previous_context == "[]":
        is_empty = True
        message = """
        ¡Hola! 👋 ¡Soy Ikusito, tu nuevo asistente virtual en la empresa!

        Estoy aquí para ayudarte a encontrar toda la información que necesites de forma rápida y sencilla. Piensa en mí como tu motor de búsqueda y tu experto en datos internos.

        🧐 ¿Qué puedo hacer por ti?
        - Responder preguntas sobre políticas, procedimientos y documentos internos.
        - Ayudarte a navegar por nuestra base de conocimiento.
        - Proporcionarte información precisa y actualizada sobre bases de datos internas.

        En resumen, si la información está dentro de la compañía, ¡la encontraré para ti!

        🚀 ¿Cómo usarme?
        Simplemente escribe tu pregunta de la forma más clara posible. Por ejemplo:
        - "¿Cuál es la política de vacaciones de la empresa?"
        - "¿Dónde puedo encontrar el manual del empleado?"
        - "¿Cuáles son los procedimientos para solicitar equipo nuevo?"

        ⛔ Importante:
        - Mi conocimiento se basa únicamente en la información disponible dentro de la empresa. No tengo acceso a datos externos ni a información personal.
        - Si no encuentro la respuesta, te lo haré saber amablemente.
        """
    else:
        is_empty = False
        message = "Continuemos con nuestra conversación. 😊"

    return {
        "user_id": user_id,
        "session_id": session_id,
        "message": message,
        "is_empty": is_empty,
        "previous_context": previous_context
    }