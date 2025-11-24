from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Modelo de Usuario
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)  # El email debe ser único
    
    # Relación con trivias (muchos a muchos a través de TriviaUsuario)
    trivias = relationship("TriviaUsuario", back_populates="usuario", cascade="all, delete-orphan")

# Modelo de Pregunta
class Pregunta(Base):
    __tablename__ = "preguntas"
    
    id = Column(Integer, primary_key=True, index=True)
    texto_pregunta = Column(String(500), nullable=False)
    # Las opciones las guardo como JSON, ejemplo: {"A": "Opción 1", "B": "Opción 2"}
    opciones = Column(JSON, nullable=False)
    respuesta_correcta = Column(String(10), nullable=False)  # "A", "B", "C", etc.
    dificultad = Column(String(20), nullable=False, index=True)  # puede ser "fácil", "medio" o "difícil"
    
    # Relación con trivias
    trivias = relationship("TriviaPregunta", back_populates="pregunta", cascade="all, delete-orphan")

# Modelo de Trivia
class Trivia(Base):
    __tablename__ = "trivias"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(String(1000), nullable=True)  # Opcional
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())  # Se crea automáticamente
    
    # Relaciones muchos a muchos con preguntas y usuarios
    preguntas = relationship("TriviaPregunta", back_populates="trivia", cascade="all, delete-orphan")
    usuarios = relationship("TriviaUsuario", back_populates="trivia", cascade="all, delete-orphan")

# Tabla intermedia para relacionar Trivia con Pregunta (muchos a muchos)
# Una trivia puede tener muchas preguntas y una pregunta puede estar en muchas trivias
class TriviaPregunta(Base):
    __tablename__ = "trivia_preguntas"
    
    id = Column(Integer, primary_key=True, index=True)
    trivia_id = Column(Integer, ForeignKey("trivias.id"), nullable=False)
    pregunta_id = Column(Integer, ForeignKey("preguntas.id"), nullable=False)
    
    # Relaciones
    trivia = relationship("Trivia", back_populates="preguntas")
    pregunta = relationship("Pregunta", back_populates="trivias")

# Tabla intermedia para relacionar Trivia con Usuario (muchos a muchos)
class TriviaUsuario(Base):
    __tablename__ = "trivia_usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    trivia_id = Column(Integer, ForeignKey("trivias.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Relaciones
    trivia = relationship("Trivia", back_populates="usuarios")
    usuario = relationship("Usuario", back_populates="trivias")

# Modelo para guardar las respuestas de los usuarios
class Participacion(Base):
    __tablename__ = "participaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    trivia_id = Column(Integer, ForeignKey("trivias.id"), nullable=False)
    pregunta_id = Column(Integer, ForeignKey("preguntas.id"), nullable=False)
    respuesta_dada = Column(String(10), nullable=False)  # La respuesta que eligió el usuario
    es_correcta = Column(Integer, default=0)  # 0 si está mal, 1 si está bien
    puntaje_obtenido = Column(Integer, default=0)  # Los puntos que ganó (según la dificultad)
    fecha_respuesta = Column(DateTime(timezone=True), server_default=func.now())  # Cuándo respondió

