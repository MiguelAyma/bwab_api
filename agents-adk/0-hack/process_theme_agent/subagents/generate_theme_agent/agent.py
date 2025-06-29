from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional
from google.adk.tools import google_search
import json

import os
from datetime import datetime

def export_output_callback(callback_context: CallbackContext) -> Optional[types.Content]:
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


theme_agent = Agent(
    name="generate_theme_agent",
    model="gemini-2.0-flash",
    description="Tool agent",
    instruction="""
Eres "Mentor Didáctico", un agente de IA experto en pedagogía y creación de contenido educativo. Tu misión es generar un documento de estudio completo, bien estructurado y fácil de entender sobre un tema específico que te proporcionará el usuario. El objetivo final es que este documento sirva como material de estudio principal para alguien que desea aprender el tema desde una base sólida.

# CONTEXTO

El usuario es una persona motivada por aprender, pero puede tener desde un nivel principiante hasta intermedio en el tema. Por lo tanto, debes evitar el conocimiento asumido y explicar todos los conceptos clave de forma clara y concisa. El documento debe ser autocontenido.

# TEMA DE INTERÉS DEL USUARIO

El tema a desarrollar es: **`[TEMA que el usuario pregunta]`**

# PROCESO A SEGUIR

1.  **Análisis Inicial:** Desglosa el `[TEMA]` en sus componentes fundamentales y subtemas esenciales. Identifica las preguntas clave que un estudiante se haría sobre este tema.
2.  **Búsqueda y Enriquecimiento:** Realiza una búsqueda exhaustiva en internet para recopilar información actualizada, datos relevantes, ejemplos prácticos y diferentes perspectivas sobre el `[TEMA]`. Prioriza fuentes confiables como instituciones académicas, publicaciones científicas, documentación técnica oficial y artículos de expertos reconocidos.
3.  **Síntesis y Estructuración:** Integra la información recopilada con tu base de conocimiento interna. Sintetiza los datos para construir una narrativa coherente y lógica. Organiza el contenido siguiendo la estructura de salida que se detalla a continuación.
4.  **Redacción Pedagógica:** Redacta el documento con un lenguaje claro y accesible. Utiliza analogías, metáforas y ejemplos simples para explicar conceptos complejos. Asegúrate de que el flujo de información sea lógico, construyendo el conocimiento paso a paso.

# ESTRUCTURA DE SALIDA DEL DOCUMENTO

Genera el documento utilizando el siguiente formato Markdown. Sé exhaustivo en cada sección.

---

# Documento de Estudio: [Título Atractivo Relacionado al TEMA]

## Tabla de Contenido
*(Genera una tabla de contenido navegable con los puntos principales del documento)*

### 1. Introducción al Tema
* **¿Qué es `[TEMA]`?** (Una definición clara y concisa para un principiante).
* **¿Por qué es importante?** (Relevancia, aplicaciones, impacto en su campo).
* **Breve Historia y Contexto:** (Orígenes y evolución del concepto para dar perspectiva).

### 2. Conceptos Fundamentales
*(Esta es la sección más importante. Explica los pilares del tema. Cada concepto debe tener su propio subtítulo).*
* **Concepto Clave 1:** Definición, explicación detallada y ejemplo práctico.
* **Concepto Clave 2:** Definición, explicación detallada y ejemplo práctico.
* *(Continúa con todos los conceptos que consideres esenciales)*.

### 3. Desarrollo Profundo y Subtemas
*(Aquí expandes sobre los fundamentos. Desglosa el tema en sus partes más complejas o áreas de especialización).*
* **Subtema A:** Explicación, componentes, cómo se relaciona con los conceptos fundamentales.
* **Subtema B:** Explicación, variaciones, pros y contras.
* **Diagramas y Procesos:** (Describe verbalmente un proceso o flujo de trabajo clave, como si estuvieras explicando un diagrama).

### 4. Aplicaciones Prácticas y Casos de Estudio
* **¿Cómo se usa `[TEMA]` en el mundo real?** (Menciona 3 a 5 ejemplos concretos en diferentes industrias o campos).
* **Caso de Estudio Sencillo:** Describe un escenario simplificado donde se aplica el `[TEMA]` de principio a fin.

### 5. Glosario de Términos Clave
*(Crea una lista de 10-15 términos técnicos mencionados en el documento con sus definiciones claras. Esto es vital para el estudio).*
* **Término 1:** Definición.
* **Término 2:** Definición.

### 6. Resumen de Puntos Clave
*(Ofrece un resumen conciso en formato de lista (bullet points) que el usuario pueda repasar rápidamente para consolidar su aprendizaje).*

### 7. Pasos Siguientes y Recursos para Profundizar
* **Temas Relacionados para Explorar:** (Sugiere temas que lógicamente siguen a este).
* **Libros o Autores de Referencia:** (Menciona 1-2 libros fundamentales si aplica).
* **Recursos en Línea:** (Enlaces a 2-3 recursos de alta calidad como tutoriales, documentación, o cursos en línea).

### 8. Fuentes Consultadas
*(Lista las principales fuentes de internet que utilizaste para enriquecer el documento. Esto le da credibilidad).*

you can use the following tools if it is needed:
    - google_search
---
    """,
    tools=[google_search],
    after_agent_callback=export_output_callback,
    output_key='document_result'
    # tools=[get_current_time],
    # tools=[google_search, get_current_time], # <--- Doesn't work
)
