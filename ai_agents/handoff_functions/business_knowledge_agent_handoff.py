from agents import handoff

def create_knowledge_base_agent_handoff(business_knowledge_agent):
  return handoff(
    agent=business_knowledge_agent,
    tool_name_override="agent_to_delegate_business_knowledge",
    tool_description_override="Herramienta personalizada para delegar la presentación de conocimiento de negocio a un agente especializado.",
  )