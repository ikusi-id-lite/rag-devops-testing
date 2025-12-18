from pydantic import BaseModel, Field

class Sql_statement_response_model(BaseModel):
  sql: str = Field(..., description="Sentencia SQL generada que cumple con la consulta del usuario")
  notes: str = Field(..., description="Breve nota sobre la lógica de la consulta o asunciones hechas")

  class ConfigDict:
    extra = "forbid"