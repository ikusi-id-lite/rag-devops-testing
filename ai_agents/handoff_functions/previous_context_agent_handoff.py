from agents import RunContextWrapper, handoff
from ..models.sql_statement_response_model import Sql_statement_response_model

def create_previous_context_agent_handoff(previous_context_agent_instance):
  return handoff(
    agent=previous_context_agent_instance,
    tool_name_override="agent_to_delegate_answer_by_context",
    tool_description_override="Herramienta personalizada para delegar la respuesta basada en el contexto previo de conversacion a un agente especializado.",
  )