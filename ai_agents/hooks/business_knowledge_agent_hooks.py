import json
import time
from typing import Any
from agents.lifecycle import AgentHooks
from agents import Agent, RunContextWrapper
from ..context.app_context import AppContext

class business_knowledge_agent_hooks(AgentHooks[AppContext]):
    """Hooks para el Agente de Conocimiento de negocio"""
    async def on_end (
        self,
        context: RunContextWrapper[AppContext], 
        agent: Agent[AppContext],
        source: Agent[AppContext],
    ) -> None:
        """Se ejecuta cada vez que este agente es invocado (incluyendo después de un handoff)."""
        print("Bk END of context agent hooks")
        #context.context.agent_final_executor = agent.name
        milisecond = time.perf_counter()
        debugging_obj = {
            "event": "agent_end",
            "agent_name": agent.name,
            "timestamp": milisecond
        }
        context.context.debugging_info.append(debugging_obj)
        context.context.timestamps.append(milisecond)
        archivo_salida="debug_log.jsonl"
        try:
            json_line = json.dumps(debugging_obj)
            with open(archivo_salida, 'a') as f:
                f.write(json_line + '\n')

        except Exception as e:
            print(f"Error al escribir en el archivo {archivo_salida}: {e}")
        pass

    async def on_start (
        self,
        context: RunContextWrapper[AppContext], 
        agent: Agent[AppContext],
    ) -> None:
        """Se ejecuta cada vez que este agente es invocado (incluyendo después de un handoff)."""
        print("Bk START of context agent hooks")
        milisecond = time.perf_counter()
        debugging_obj = {
            "event": "agent_start",
            "agent_name": agent.name,
            "timestamp": milisecond
        }
        context.context.debugging_info.append(debugging_obj)
        context.context.timestamps.append(milisecond)
        archivo_salida="debug_log.jsonl"
        try:
            json_line = json.dumps(debugging_obj)
            with open(archivo_salida, 'a') as f:
                f.write(json_line + '\n')
        except Exception as e:
            print(f"Error al escribir en el archivo {archivo_salida}: {e}")
        pass