from pydantic import BaseModel, Field

class Tema(BaseModel):
    titulo: str = Field(
        ...,
        description="Título del tema que debe comenzar con un emoji que represente el tema"
    )
    
    content: str = Field(...)

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional
from google.adk.tools import google_search
import json

import os
from datetime import datetime

def export_output_json(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback que se ejecuta después del agente para exportar el output a un archivo TXT.
    Siempre devuelve None para mantener el flujo normal y usar la respuesta original del agente.
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()
    final_report = callback_context.state.get("document_result", "sin resultado disponible")
    
    # Obtener el output original del agente (si está disponible)
    # Nota: El output real del agente no está directamente disponible en el callback_context
    # pero podemos capturar información del contexto
    
    print(f"\n[Export Callback] Procesando salida del agente: {agent_name}")
    
    # Preparar datos para exportar
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "agent_name": agent_name,
        "invocation_id": invocation_id,
        "session_state": current_state,
        "context_info": {
            "has_state": bool(current_state),
            "state_keys": list(current_state.keys()) if current_state else []
        }
    }
    
    # Crear el nombre del archivo con timestamp
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"agent_output_{agent_name}_{timestamp_str}.txt"
    
    # Crear directorio de outputs si no existe
    output_dir = "agent_outputs"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    # Exportar a archivo TXT
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("GOOGLE ADK AGENT OUTPUT EXPORT\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Timestamp: {export_data['timestamp']}\n")
            f.write(f"Agent Name: {export_data['agent_name']}\n")
            f.write(f"Invocation ID: {export_data['invocation_id']}\n")
            f.write(f"Export File: {filename}\n\n")
            
            f.write("-" * 40 + "\n")
            f.write("SESSION STATE:\n")
            f.write("-" * 40 + "\n")
            if current_state:
                f.write(json.dumps(current_state, indent=2, ensure_ascii=False))
            else:
                f.write("No session state available")
            f.write("\n\n")
            
            f.write("-" * 40 + "\n")
            f.write("CONTEXT INFORMATION:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Has State: {export_data['context_info']['has_state']}\n")
            f.write(f"State Keys: {export_data['context_info']['state_keys']}\n\n")
            
            f.write("-" * 40 + "\n")
            f.write("NOTES:\n")
            f.write("-" * 40 + "\n")
            f.write("- Este callback se ejecuta DESPUÉS del agente\n")
            f.write("- El output original del agente se mantiene (callback devuelve None)\n")
            f.write("- Los datos del contexto y estado de sesión se han exportado\n")
            f.write("- Para capturar el texto de respuesta del agente, se necesitaría\n")
            f.write("  implementar un mecanismo adicional de captura\n\n")
            
            f.write("="*60 + "\n")
            f.write("END OF EXPORT\n")
            f.write("="*60 + "\n")

            # final report
            f.write(f"fthe final report is: {final_report}")
        
        print(f"[Export Callback] ✅ Output exportado exitosamente a: {filepath}")
        
    except Exception as e:
        print(f"[Export Callback] ❌ Error al exportar: {str(e)}")
    
    # IMPORTANTE: Devolver None para mantener el flujo normal
    # Esto permite que se use la respuesta original del agente
    return None




themejson_agent = Agent(
    name="generate_themejson_agent",
    model="gemini-2.0-flash",
    description="Tool agent",
    instruction="""
    Your are an assistant that recieves a document of a topic you only function is to estructure the content following the schema
    you are not able to edit or modify the content of the document, you only can structure it in the schema provided.
    """,
    after_agent_callback=export_output_json,
    output_key='documentjson_result',
    output_schema=Tema
    # tools=[get_current_time],
    # tools=[google_search, get_current_time], # <--- Doesn't work
)
