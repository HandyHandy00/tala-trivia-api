from pydantic import BaseModel, EmailStr, Field
from typing import Dict, List, Optional
from datetime import datetime

# Schemas para Usuario
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., description="Nombre del usuario", example="Maxi")
    email: EmailStr = Field(..., description="Email del usuario", example="maxi17arias@gmail.com")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Maxi",
                "email": "maxi17arias@gmail.com"
            }
        }

# Schema para devolver un usuario (con el ID que se genera automáticamente)
class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    
    class Config:
        from_attributes = True  # Para convertir desde el modelo de SQLAlchemy

# Schemas para Pregunta
class PreguntaCreate(BaseModel):
    texto_pregunta: str = Field(..., description="Texto de la pregunta", example="¿Cuál es el proceso de selección más efectivo?")
    opciones: Dict[str, str] = Field(..., description="Opciones de respuesta", example={"A": "Entrevista telefónica", "B": "Entrevista presencial", "C": "Evaluación técnica", "D": "Combinación de métodos"})
    respuesta_correcta: str = Field(..., description="Respuesta correcta (A, B, C, D, etc.)", example="D")
    dificultad: str = Field(..., description="Nivel de dificultad: fácil, medio, difícil", example="fácil")
    
    class Config:
        json_schema_extra = {
            "example": {
                "texto_pregunta": "¿Cuál es el proceso de selección más efectivo?",
                "opciones": {
                    "A": "Entrevista telefónica",
                    "B": "Entrevista presencial",
                    "C": "Evaluación técnica",
                    "D": "Combinación de métodos"
                },
                "respuesta_correcta": "D",
                "dificultad": "fácil"
            }
        }

class PreguntaResponse(BaseModel):
    id: int
    texto_pregunta: str
    opciones: Dict[str, str]
    respuesta_correcta: str
    dificultad: str
    
    class Config:
        from_attributes = True

# Schemas para Trivia
class TriviaCreate(BaseModel):
    nombre: str = Field(..., description="Nombre de la trivia", example="Trivia de Recursos Humanos")
    descripcion: Optional[str] = Field(None, description="Descripción de la trivia", example="Preguntas sobre procesos de RRHH")
    pregunta_ids: List[int] = Field(..., description="Lista de IDs de preguntas", example=[1, 2, 3])
    usuario_ids: List[int] = Field(..., description="Lista de IDs de usuarios", example=[1, 2])
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Trivia de Recursos Humanos",
                "descripcion": "Preguntas sobre procesos de RRHH",
                "pregunta_ids": [1, 2, 3],
                "usuario_ids": [1, 2]
            }
        }

class TriviaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

# Schema para mostrar preguntas a los jugadores
# IMPORTANTE: No incluye la respuesta correcta ni la dificultad
# según lo que dice el enunciado
class PreguntaJugador(BaseModel):
    id: int
    texto_pregunta: str
    opciones: Dict[str, str]
    # No incluyo respuesta_correcta ni dificultad aquí
    
    class Config:
        from_attributes = True

# Schemas para Participación (cuando un usuario responde)
class ParticipacionCreate(BaseModel):
    usuario_id: int = Field(..., description="ID del usuario")
    trivia_id: int = Field(..., description="ID de la trivia")
    pregunta_id: int = Field(..., description="ID de la pregunta")
    respuesta_dada: str = Field(..., description="La respuesta que eligió el usuario (A, B, C, D, etc.)", example="D")
    
    class Config:
        json_schema_extra = {
            "example": {
                "usuario_id": 1,
                "trivia_id": 1,
                "pregunta_id": 1,
                "respuesta_dada": "D"
            }
        }

class ParticipacionResponse(BaseModel):
    id: int
    usuario_id: int
    trivia_id: int
    pregunta_id: int
    respuesta_dada: str
    es_correcta: int
    puntaje_obtenido: int
    fecha_respuesta: datetime
    
    class Config:
        from_attributes = True

# Schemas para el Ranking
class RankingItem(BaseModel):
    posicion: int  # La posición en el ranking (1, 2, 3, etc.)
    usuario_id: int
    usuario_nombre: str
    puntaje_total: int  # Puntos totales que obtuvo

class RankingResponse(BaseModel):
    trivia_id: int
    trivia_nombre: str
    ranking: List[RankingItem]  # Lista ordenada de mayor a menor puntaje

