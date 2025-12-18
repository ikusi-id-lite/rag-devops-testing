from pydantic import BaseModel, Field
from typing import List, Any, Union

CellValue = Union[str, int, float, bool, None]

class Sql_execute_response_model(BaseModel):
    """
    Modelo de respuesta para la ejecución de una sentencia SQL.
    """
    columns: List[str] = Field(..., description="Lista de los nombres de las columnas del resultado de la consulta SQL")
    rows: List[List[CellValue]] = Field(..., description="Lista de listas que representan las filas de datos del resultado de la consulta SQL")

    class ConfigDict:
        extra = "forbid"