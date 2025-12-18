from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from ..context.app_context import AppContext
from ..hooks.previous_context_agent_hooks import previous_context_agent_hooks
from ..models.previous_context_response_model import previous_context_response_model
from agents.agent_output import AgentOutputSchema
from openai.types.shared import Reasoning
from agents import ModelSettings

async def previous_context_dynamic_instructions(
    context: RunContextWrapper[AppContext], agent: Agent[AppContext]
) -> str:
    prompt = f"""{RECOMMENDED_PROMPT_PREFIX}
    # Contexto previo de conversacion:
    {context.context.previous_context}
    # ROL
    Eres un agente especializado en responder preguntas utilizando exclusivamente el contexto previo de conversacion proporcionado.

    # Objetivos principales
      - Debes usar el contexto previo de conversacion para responder.
      - La respuesta debe darse en el formato establecido (Json encontrado en el contexto previo de conversacion).
      - No se debe responde con información fuera del contexto previo de conversacion.

    # FORMATO DE SALIDA (JSON ESTRICTO)
    El JSON de salida debe contener el objeto data encontrado en el **contexto previo de conversacion** que mas corresponda a la solucion de la pregunta del usuario.
    """
    return prompt


def create_previous_context_agent(app_context) -> Agent:
  return Agent[app_context](
    name="Agente de respuesta por contexto",
    instructions=previous_context_dynamic_instructions,
    hooks=previous_context_agent_hooks(),
    output_type=AgentOutputSchema(previous_context_response_model, strict_json_schema=False),
    model="gpt-5-mini",
    model_settings=ModelSettings(reasoning=Reasoning(effort="medium"), verbosity="medium")
  )