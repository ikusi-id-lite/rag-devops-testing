from pydantic import BaseModel, Field
from typing import Union


class out_of_context_data(BaseModel):
    type: str = Field(..., description="Tipo de presentación, siempre sera 'paragraph'")
    user_query: str = Field(..., description="Pregunta original del usuario")
    answer: str = Field(..., description="Respuesta en lenguaje natural, amena y comprensible, explicando que la consulta está fuera del contexto empresarial y sugiriendo reformular la pregunta.")

class Out_of_context_response_model(BaseModel):
    """
    Modelo de respuesta fuera de contexto
    """
    data: Union[out_of_context_data] = Field(...,
        description="El resultado "
    )