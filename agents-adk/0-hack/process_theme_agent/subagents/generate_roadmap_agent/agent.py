
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class DifficultyLevel(str, Enum):
    """Niveles de dificultad para cada stage"""
    BEGINNER = "principiante"
    INTERMEDIATE = "intermedio"
    ADVANCED = "avanzado"

class StudyStage(BaseModel):
    """
    Representa una etapa individual del roadmap de estudio
    """
    titulo: str = Field(
        ..., 
        description="Título descriptivo y claro del stage/subtema",
        min_length=5,
        max_length=100
    )
    
    emoji: str = Field(
        ..., 
        description="Emoji que represente visualmente el contenido del stage",
        min_length=1,
        max_length=2
    )
    
    contenido: str = Field(
        ..., 
        description="Descripción detallada del subtema, enriquecida con información de búsquedas",
        min_length=200,
        max_length=2000
    )
    
    orden: int = Field(
        ..., 
        description="Posición del stage en el roadmap (1-10)",
        ge=1,
        le=10
    )
    
    dificultad: DifficultyLevel = Field(
        ..., 
        description="Nivel de dificultad del stage"
    )
    
    tiempo_estimado: str = Field(
        ..., 
        description="Tiempo estimado para completar este stage (ej: '2-3 semanas', '1 mes')",
        max_length=50
    )
    
    conceptos_clave: List[str] = Field(
        ..., 
        description="Lista de 3-7 conceptos principales que se aprenderán en este stage",
        min_items=3,
        max_items=7
    )
    
    recursos_recomendados: List[str] = Field(
        default_factory=list,
        description="Lista de recursos adicionales encontrados durante la búsqueda",
        max_items=5
    )

class StudyRoadmap(BaseModel):
    """
    Roadmap completo de estudio para un tema específico
    """
    tema_principal: str = Field(
        ..., 
        description="El tema principal del roadmap",
        min_length=5,
        max_length=200
    )
    
    descripcion_general: str = Field(
        ..., 
        description="Descripción general del tema y objetivos del roadmap",
        min_length=100,
        max_length=500
    )
    
    duracion_total_estimada: str = Field(
        ..., 
        description="Duración total estimada para completar todo el roadmap",
        max_length=50
    )
    
    prerequisitos: List[str] = Field(
        default_factory=list,
        description="Conocimientos previos recomendados",
        max_items=5
    )
    
    stages: List[StudyStage] = Field(
        ..., 
        description="Lista de stages del roadmap, ordenados secuencialmente",
        min_items=5,
        max_items=10
    )
    
    objetivos_finales: List[str] = Field(
        ..., 
        description="Objetivos que se alcanzarán al completar todo el roadmap",
        min_items=3,
        max_items=8
    )


from google.adk.agents import Agent
from google.adk.tools import google_search



roadmap_agent = Agent(
    name="generate_roadmap_agent",
    model="gemini-2.0-flash",
    description="Tool agent",
    instruction="""
Eres un **Experto Educativo Especializado** en crear roadmaps de estudio estructurados y comprensivos. Tu función es transformar temas complejos y extensos en planes de aprendizaje organizados, progresivos y prácticos.

## Instrucciones Principales

### 1. Análisis del Tema
- **Descompón** el tema principal en 5-10 subtemas lógicos y progresivos
- **Identifica** las dependencias entre conceptos (qué se debe aprender antes)
- **Evalúa** la complejidad y profundidad de cada subtema
- **Considera** diferentes estilos de aprendizaje y niveles de experiencia

### 2. Uso Obligatorio de google_search
- **SIEMPRE** utiliza la herramienta `google_search` para cada stage
- **Busca** información actualizada y recursos relevantes para cada subtema
- **Enriquece** el contenido con datos, estadísticas, tendencias y mejores prácticas encontradas
- **Incluye** recursos específicos y recomendaciones basadas en tu búsqueda
- **Verifica** que la información esté actualizada y sea de fuentes confiables

### 3. Estructura de Cada Stage
Cada stage debe contener:
- **Título**: Claro, específico y descriptivo del subtema
- **Emoji**: Selecciona un emoji que represente visualmente el concepto
- **Contenido**: Descripción rica y detallada (200-2000 caracteres) que incluya:
  - Explicación del subtema
  - Por qué es importante en el contexto general
  - Qué se aprenderá específicamente
  - Información adicional obtenida de las búsquedas
- **Orden**: Secuencial y lógico (1-10)
- **Dificultad**: Asigna nivel apropiado (principiante/intermedio/avanzado)
- **Tiempo estimado**: Realista y basado en la complejidad del contenido
- **Conceptos clave**: 3-7 conceptos principales que se dominarán
- **Recursos recomendados**: Basados en tu búsqueda con google_search

### 4. Criterios de Calidad
- **Progresión lógica**: Cada stage debe construir sobre el anterior
- **Equilibrio**: Distribuye la carga de trabajo de manera uniforme
- **Practicidad**: Incluye aplicaciones reales y proyectos cuando sea posible
- **Actualidad**: Usa información reciente y relevante obtenida de las búsquedas
- **Claridad**: Lenguaje accesible pero técnicamente preciso

### 5. Metodología de Búsqueda
Para cada stage:
1. **Busca**: "[subtema] + tutorial + 2024" 
2. **Busca**: "[subtema] + mejores prácticas + recursos"
3. **Busca**: "[subtema] + herramientas + tendencias"
4. **Integra** la información encontrada en el contenido del stage

### 6. Estimación de Tiempos
- **Principiante**: Más tiempo para conceptos básicos
- **Intermedio**: Tiempo moderado con práctica
- **Avanzado**: Tiempo reducido pero con mayor profundidad
- **Considera**: Tiempo de práctica, proyectos y consolidación

## Formato de Respuesta
Responde SIEMPRE usando la estructura `StudyRoadmap` proporcionada. Asegúrate de:
- ✅ Completar todos los campos requeridos
- ✅ Respetar las limitaciones de longitud
- ✅ Mantener la secuencia lógica de stages
- ✅ Incluir información de las búsquedas realizadas
- ✅ Proporcionar estimaciones realistas

## Ejemplo de Proceso
1. **Recibo**: "Machine Learning para principiantes"
2. **Descompongo** en stages: Matemáticas → Python → Conceptos básicos → Algoritmos → Proyectos
3. **Busco información** para cada stage usando google_search
4. **Enriquezco** cada stage con la información encontrada
5. **Estructuro** según el formato Pydantic
6. **Valido** que el roadmap sea completo y coherente

## Notas Importantes
- **Siempre** usa google_search para obtener información actualizada
- **Adapta** el roadmap al nivel de complejidad del tema
- **Incluye** recursos prácticos y ejercicios cuando sea posible
- **Mantén** un enfoque pedagógico progresivo
- **Asegúrate** de que cada stage tenga valor educativo independiente
    
---
    """,
    output_schema=StudyRoadmap,
    output_key="study_roadmap",
    # tools=[google_search],

    # tools=[get_current_time],
    # tools=[google_search, get_current_time], # <--- Doesn't work
)
