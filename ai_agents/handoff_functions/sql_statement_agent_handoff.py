from agents import handoff

def create_sql_statement_agent_handoff(sql_statement_agent):
  return handoff(
    agent=sql_statement_agent,
    tool_name_override="agent_to_delegate_sql_generation",
    tool_description_override="Herramienta personalizada para delegar la generación de sentencias SQL a un agente especializado",
  )