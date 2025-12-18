from agents import RunContextWrapper, handoff
from ..models.sql_execute_response_model import Sql_execute_response_model


async def on_handoff(ctx: RunContextWrapper[None], input_data: Sql_execute_response_model):
  print(f"Generando especificación de gráfico para: columnas= {input_data.columns}")


def create_presentation_agent_handoff(presentation_agent_instance):
  return handoff(
    agent=presentation_agent_instance,
    tool_name_override="agent_to_delegate_presentation",
    tool_description_override="**PRIORIDAD:** Agente especializado para delegar la presentación de datos obtenidos",
    on_handoff=on_handoff,
    input_type=Sql_execute_response_model,
  )