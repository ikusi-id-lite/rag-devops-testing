from agents import RunContextWrapper, handoff
from ..models.sql_statement_response_model import Sql_statement_response_model


async def on_handoff(ctx: RunContextWrapper[None], input_data: Sql_statement_response_model):
  print(f"La sentencia SQL a ejecutar es: {input_data.sql} \n Notas: {input_data.notes}")


def create_sql_execute_handoff(execute_sql_agent_instance):
  return handoff(
    agent=execute_sql_agent_instance,
    tool_name_override="agent_to_delegate_sql_execution",
    tool_description_override="**PRIORIDAD:** Agente especializado para delegar la ejecución de sentencias SQL y obtener resultados. Usar siempre que se necesite ejecutar una sentencia SQL válida.",
    on_handoff=on_handoff,
    input_type=Sql_statement_response_model,
  )