from agents import handoff

def create_out_of_context_agent_handoff(out_of_context_agent_instance):
  return handoff(
    agent=out_of_context_agent_instance,
    tool_name_override="agent_to_delegate_answer_out_of_context",
    tool_description_override="Herramienta personalizada para delegar la respuesta basada de preguntas fuera de contexto empresarial o de conversacion previa",
  )