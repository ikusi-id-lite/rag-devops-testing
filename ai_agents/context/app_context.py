from dataclasses import dataclass, field

@dataclass
class AppContext:
    """
    Contexto de la aplicación que se comparte entre los agentes.
    """
    user_query: str
    previous_context: str
    logged_user_rol: str
    timestamps: list = field(default_factory=list)
    debugging_info: list = field(default_factory=list)