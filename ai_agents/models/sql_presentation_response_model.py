from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Any, Optional, Union

CellValue = Union[str, int, float, bool, None, Dict[str, Any]]

class Mapping(BaseModel):
    """Representa las claves para los ejes x e y del gráfico."""
    x_key: str
    y_key: str

class presentation_chart_model(BaseModel):
    """
    Modelo de respuesta para la ejecución de una sentencia SQL con especificación de gráfico.
    """
    user_query: str = Field(..., description="Pregunta original del usuario")
    sql_statement: str = Field(..., description="Sentencia SQL ejecutada")
    model_config = ConfigDict(extra='forbid', strict=True)
    columns: list[str] = Field(..., description="Lista de los nombres de las columnas del resultado de la consulta SQL")
    rows: list[list[CellValue]] = Field(..., description="Lista que representan las filas de datos del resultado de la consulta SQL")
    type: str = Field(..., description="Tipo de gráfico a utilizar para la visualización")
    details: str = Field(..., description="Breve justificación sobre el tipo seleccionado.")
    mapping: Optional[Mapping] = Field(None, description="Mapeo de datos para gráficos, si aplica.")
    answer: str = Field(..., description="Presentacion agradable del grafico en lenguaje natural.")


class presentation_paragraph_model(BaseModel):
    """
    Modelo de respuesta para una ejecución de una sentencia SQL que se expresa en párrafo.
    """
    user_query: str = Field(..., description="Pregunta original del usuario")
    sql_statement: str = Field(..., description="Sentencia SQL ejecutada")
    model_config = ConfigDict(extra='forbid', strict=True)
    columns: list[str] = Field(..., description="Lista de los nombres de las columnas del resultado de la consulta SQL")
    rows: list[list[CellValue]] = Field(..., description="Lista que representan las filas de datos del resultado de la consulta SQL")
    type: str = Field(..., description="Tipo de gráfico a utilizar para la visualización")
    details: str = Field(..., description="Breve justificación sobre el tipo seleccionado.")
    answer: str = Field(..., description="Presentacion de la información en lenguaje natural.")


class presentation_response_model(BaseModel):
    """
    Modelo de respuesta que envuelve el resultado.
    """
    data: Union[presentation_chart_model, presentation_paragraph_model] = Field(...,
        description="El resultado real de la presentación, que es un gráfico o un párrafo."
    )