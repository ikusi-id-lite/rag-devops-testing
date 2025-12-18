from pydantic import BaseModel, Field, ConfigDict
from typing import Union

class bk_db_data(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    type: str = Field(..., description="Tipo de presentación, siempre sera 'paragraph'")
    user_query: str = Field(..., description="Pregunta original del usuario")
    answer: str = Field(..., description="Presentacion de la información en lenguaje natural, amena y comprensible.")
    info_source: str = Field(..., description="Fuente de la información utilizada para generar la respuesta.")


class presentation_business_knowledge_model(BaseModel):
    """
    Modelo de respuesta para la presentación del conocimiento de negocio.
    """

    data: Union[bk_db_data] = Field(...,
        description="El resultado real de la presentación, que es un gráfico o un párrafo."
    )

    """ class ConfigDict:
        extra = "forbid" """
