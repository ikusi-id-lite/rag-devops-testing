from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from ..hooks.sql_execute_agent_hooks import sql_execute_agent_hooks
from ..models.sql_execute_response_model import Sql_execute_response_model
from ..context.app_context import AppContext
from openai.types.shared import Reasoning
from agents import ModelSettings

async def sql_execute_agent_dynamic_instructions(
    context: RunContextWrapper[AppContext], agent: Agent[AppContext]
) -> str:
    prompt = f"""{RECOMMENDED_PROMPT_PREFIX}
      # Rol
      Eres un **Agente que ejecuta sentencias SQL**
      # Obejtivos principales
      - Ejecutar la sentencia SQL proporcionada y obtener las filas y columnas resultantes Usando la herramienta 'clean_and_execute_statement' para la ejecución. (PRIORIDAD MAXIMA!)
      - Formatear los resultados obtenidos en un objeto JSON con la Estructura de Datos especificada. (PRIORIDAD MAXIMA!)
      - Delegar los resultados al siguiente agente encargado de la presentación de datos. (PRIORIDAD MAXIMA!)

      # Informacion necesaria para realizar la ejecucion de la sentencia SQL
      ## Rol de Usuario Logueado: {context.context.logged_user_rol}

      # Flujo de Trabajo (OBLIGATORIO)
      1.  **Ejecutar** la sentencia SQL usando la herramienta 'clean_and_execute_statement'.
      2.  **Formatear** los resultados obtenidos (columnas y filas) con la Estructura de Datos para delegar.
      3.  **Delegar/Handoff** el JSON de resultados completo al agente de presentación. Este es el **ÚLTIMO PASO** y no debe haber ninguna otra salida de texto.

      # Estructura de Datos (JSON Estricto - Contenido a Delegar - Obligatorio)
      El contenido que se va a delegar debe ser un objeto JSON **VÁLIDO y COMPLETO** con los siguientes campos:
      {{
          "columns": ["nombre_columna_1", "nombre_columna_2", ...],
          "rows": [
              ["valor_fila_1_columna_1", "valor_fila_1_columna_2", ...],
              ["valor_fila_2_columna_1", "valor_fila_2_columna_2", ...],
              ...
          ]
      }}

      # ACCIÓN FINAL Y OBLIGATORIA (DELEGACIÓN / HANDOFF)
      Una vez que hayas ejecutado la sentencia SQL y preparado el contenido según la 'Estructura de Datos' anterior, **DEBES, sin excepción, usar la herramienta de delegar la presentacion al Agente de Presentación de Resultados.**

      **Simplemente DELEGA. No generes ninguna explicación o texto de respuesta.**
    """
    return prompt


def create_sql_execute_agent(app_context: type, mcp_servers: list, handoffs: list) -> Agent:
  return Agent[app_context](
    name="Agente de ejecucion de Bases de Datos",
    instructions=sql_execute_agent_dynamic_instructions,
    mcp_servers=mcp_servers,
    output_type=Sql_execute_response_model,
    hooks=sql_execute_agent_hooks(),
    handoffs=handoffs,
    model="gpt-5-mini",
    model_settings=ModelSettings(reasoning=Reasoning(effort="low"), verbosity="low")
  )