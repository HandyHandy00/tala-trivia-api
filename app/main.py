from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import engine, Base, get_db
from app.models import Usuario, Pregunta, Trivia, TriviaPregunta, TriviaUsuario, Participacion
from app.schemas import (
    UsuarioCreate, UsuarioResponse, 
    PreguntaCreate, PreguntaResponse, PreguntaJugador,
    TriviaCreate, TriviaResponse,
    ParticipacionCreate, ParticipacionResponse,
    RankingResponse, RankingItem
)

# Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="TalaTrivia API",
    description="API para gestionar trivias de recursos humanos",
    version="1.0.0"
)

# Endpoint básico para verificar que la API está funcionando
@app.get("/")
def read_root():
    return {
        "message": "¡Bienvenido a TalaTrivia API!",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Endpoint de health check
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API funcionando correctamente"}

# ============================================
# ENDPOINTS DE USUARIOS
# ============================================

@app.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo usuario"""
    # Primero verifico si el email ya existe para evitar duplicados
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear el nuevo usuario
    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email
    )
    
    # Guardar en la base de datos
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)  # Para obtener el ID que se generó
    
    return nuevo_usuario

@app.get("/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    """Listar todos los usuarios"""
    usuarios = db.query(Usuario).all()
    return usuarios

@app.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtener un usuario específico por su ID"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    return usuario

# ============================================
# ENDPOINTS DE PREGUNTAS
# ============================================

@app.post("/preguntas", response_model=PreguntaResponse, status_code=status.HTTP_201_CREATED)
def crear_pregunta(pregunta: PreguntaCreate, db: Session = Depends(get_db)):
    """Crear una nueva pregunta"""
    # Validar que la respuesta correcta esté dentro de las opciones disponibles
    if pregunta.respuesta_correcta not in pregunta.opciones:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La respuesta correcta debe estar en las opciones"
        )
    
    # Validar que la dificultad sea una de las permitidas
    dificultades_validas = ["fácil", "medio", "difícil"]
    if pregunta.dificultad not in dificultades_validas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La dificultad debe ser una de: {', '.join(dificultades_validas)}"
        )
    
    nueva_pregunta = Pregunta(
        texto_pregunta=pregunta.texto_pregunta,
        opciones=pregunta.opciones,
        respuesta_correcta=pregunta.respuesta_correcta,
        dificultad=pregunta.dificultad
    )
    
    db.add(nueva_pregunta)
    db.commit()
    db.refresh(nueva_pregunta)
    
    return nueva_pregunta

@app.get("/preguntas", response_model=List[PreguntaResponse])
def listar_preguntas(db: Session = Depends(get_db)):
    """Listar todas las preguntas"""
    preguntas = db.query(Pregunta).all()
    return preguntas

@app.get("/preguntas/{pregunta_id}", response_model=PreguntaResponse)
def obtener_pregunta(pregunta_id: int, db: Session = Depends(get_db)):
    """Obtener una pregunta específica por su ID"""
    pregunta = db.query(Pregunta).filter(Pregunta.id == pregunta_id).first()
    if not pregunta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pregunta con ID {pregunta_id} no encontrada"
        )
    return pregunta

# ============================================
# ENDPOINTS DE TRIVIAS
# ============================================

@app.post("/trivias", response_model=TriviaResponse, status_code=status.HTTP_201_CREATED)
def crear_trivia(trivia: TriviaCreate, db: Session = Depends(get_db)):
    """Crear una nueva trivia y asignarle preguntas y usuarios"""
    # Verificar que todas las preguntas existan
    preguntas = db.query(Pregunta).filter(Pregunta.id.in_(trivia.pregunta_ids)).all()
    if len(preguntas) != len(trivia.pregunta_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alguna pregunta no existe"
        )
    
    # Verificar que todos los usuarios existan
    usuarios = db.query(Usuario).filter(Usuario.id.in_(trivia.usuario_ids)).all()
    if len(usuarios) != len(trivia.usuario_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Algún usuario no existe"
        )
    
    # Crear la trivia
    nueva_trivia = Trivia(
        nombre=trivia.nombre,
        descripcion=trivia.descripcion
    )
    db.add(nueva_trivia)
    db.commit()
    db.refresh(nueva_trivia)
    
    # Asignar preguntas a la trivia
    for pregunta_id in trivia.pregunta_ids:
        trivia_pregunta = TriviaPregunta(
            trivia_id=nueva_trivia.id,
            pregunta_id=pregunta_id
        )
        db.add(trivia_pregunta)
    
    # Asignar usuarios a la trivia
    for usuario_id in trivia.usuario_ids:
        trivia_usuario = TriviaUsuario(
            trivia_id=nueva_trivia.id,
            usuario_id=usuario_id
        )
        db.add(trivia_usuario)
    
    db.commit()
    db.refresh(nueva_trivia)
    
    return nueva_trivia

@app.get("/trivias", response_model=List[TriviaResponse])
def listar_trivias(db: Session = Depends(get_db)):
    """Listar todas las trivias"""
    trivias = db.query(Trivia).all()
    return trivias

@app.get("/trivias/{trivia_id}", response_model=TriviaResponse)
def obtener_trivia(trivia_id: int, db: Session = Depends(get_db)):
    """Obtener una trivia específica por su ID"""
    trivia = db.query(Trivia).filter(Trivia.id == trivia_id).first()
    if not trivia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trivia con ID {trivia_id} no encontrada"
        )
    return trivia

# ============================================
# ENDPOINTS DE PARTICIPACIÓN
# ============================================

@app.get("/trivias/{trivia_id}/usuario/{usuario_id}/preguntas", response_model=List[PreguntaJugador])
def ver_trivia_jugador(trivia_id: int, usuario_id: int, db: Session = Depends(get_db)):
    """Ver las preguntas de una trivia asignada a un usuario (SIN respuesta correcta ni dificultad)"""
    # Verificar que el usuario esté asignado a esta trivia
    asignacion = db.query(TriviaUsuario).filter(
        TriviaUsuario.trivia_id == trivia_id,
        TriviaUsuario.usuario_id == usuario_id
    ).first()
    
    if not asignacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no está asignado a esta trivia"
        )
    
    # Obtener todas las preguntas que pertenecen a esta trivia
    trivia_preguntas = db.query(TriviaPregunta).filter(
        TriviaPregunta.trivia_id == trivia_id
    ).all()
    
    # Construir la lista de preguntas pero SIN mostrar la respuesta correcta ni la dificultad
    # Esto es importante según el enunciado
    preguntas_jugador = []
    for tp in trivia_preguntas:
        pregunta = db.query(Pregunta).filter(Pregunta.id == tp.pregunta_id).first()
        if pregunta:
            preguntas_jugador.append(PreguntaJugador(
                id=pregunta.id,
                texto_pregunta=pregunta.texto_pregunta,
                opciones=pregunta.opciones
                # No incluyo respuesta_correcta ni dificultad
            ))
    
    return preguntas_jugador

@app.post("/trivias/{trivia_id}/responder", response_model=ParticipacionResponse, status_code=status.HTTP_201_CREATED)
def responder_pregunta(trivia_id: int, participacion: ParticipacionCreate, db: Session = Depends(get_db)):
    """Responder una pregunta de una trivia. Calcula automáticamente si es correcta y el puntaje."""
    # Verificar que la trivia existe
    trivia = db.query(Trivia).filter(Trivia.id == trivia_id).first()
    if not trivia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trivia con ID {trivia_id} no encontrada"
        )
    
    # Verificar que el usuario esté asignado a la trivia
    asignacion = db.query(TriviaUsuario).filter(
        TriviaUsuario.trivia_id == trivia_id,
        TriviaUsuario.usuario_id == participacion.usuario_id
    ).first()
    
    if not asignacion:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no está asignado a esta trivia"
        )
    
    # Verificar que la pregunta pertenece a la trivia
    pregunta_en_trivia = db.query(TriviaPregunta).filter(
        TriviaPregunta.trivia_id == trivia_id,
        TriviaPregunta.pregunta_id == participacion.pregunta_id
    ).first()
    
    if not pregunta_en_trivia:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La pregunta no pertenece a esta trivia"
        )
    
    # Verificar si ya respondió esta pregunta
    participacion_existente = db.query(Participacion).filter(
        Participacion.usuario_id == participacion.usuario_id,
        Participacion.trivia_id == trivia_id,
        Participacion.pregunta_id == participacion.pregunta_id
    ).first()
    
    if participacion_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has respondido esta pregunta"
        )
    
    # Obtener la pregunta para validar respuesta y calcular puntaje
    pregunta = db.query(Pregunta).filter(Pregunta.id == participacion.pregunta_id).first()
    
    # Verificar si la respuesta es correcta comparando con la respuesta correcta de la pregunta
    es_correcta = 1 if participacion.respuesta_dada == pregunta.respuesta_correcta else 0
    
    # Calcular el puntaje según la dificultad
    # Fácil = 1 punto, Medio = 2 puntos, Difícil = 3 puntos
    # Solo se otorgan puntos si la respuesta es correcta
    puntajes = {
        "fácil": 1,
        "medio": 2,
        "difícil": 3
    }
    if es_correcta:
        puntaje_obtenido = puntajes.get(pregunta.dificultad, 0)
    else:
        puntaje_obtenido = 0
    
    # Crear la participación
    nueva_participacion = Participacion(
        usuario_id=participacion.usuario_id,
        trivia_id=trivia_id,
        pregunta_id=participacion.pregunta_id,
        respuesta_dada=participacion.respuesta_dada,
        es_correcta=es_correcta,
        puntaje_obtenido=puntaje_obtenido
    )
    
    db.add(nueva_participacion)
    db.commit()
    db.refresh(nueva_participacion)
    
    return nueva_participacion

@app.get("/trivias/{trivia_id}/usuario/{usuario_id}/puntaje")
def obtener_puntaje_usuario(trivia_id: int, usuario_id: int, db: Session = Depends(get_db)):
    """Obtener el puntaje total de un usuario en una trivia"""
    # Obtener todas las participaciones del usuario en esta trivia
    participaciones = db.query(Participacion).filter(
        Participacion.trivia_id == trivia_id,
        Participacion.usuario_id == usuario_id
    ).all()
    
    # Sumar todos los puntajes
    puntaje_total = sum(p.puntaje_obtenido for p in participaciones)
    
    return {
        "usuario_id": usuario_id,
        "trivia_id": trivia_id,
        "puntaje_total": puntaje_total,
        "total_respuestas": len(participaciones),
        "respuestas_correctas": sum(1 for p in participaciones if p.es_correcta == 1)
    }

# ============================================
# ENDPOINT DE RANKING
# ============================================

@app.get("/trivias/{trivia_id}/ranking", response_model=RankingResponse)
def obtener_ranking(trivia_id: int, db: Session = Depends(get_db)):
    """Obtener el ranking de usuarios en una trivia (ordenado de mayor a menor puntaje)"""
    # Verificar que la trivia existe
    trivia = db.query(Trivia).filter(Trivia.id == trivia_id).first()
    if not trivia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trivia con ID {trivia_id} no encontrada"
        )
    
    # Obtener todos los usuarios que están asignados a esta trivia
    asignaciones = db.query(TriviaUsuario).filter(
        TriviaUsuario.trivia_id == trivia_id
    ).all()
    
    # Calcular el puntaje total de cada usuario
    ranking_items = []
    for asignacion in asignaciones:
        usuario = db.query(Usuario).filter(Usuario.id == asignacion.usuario_id).first()
        
        # Buscar todas las respuestas que este usuario dio en esta trivia
        participaciones = db.query(Participacion).filter(
            Participacion.trivia_id == trivia_id,
            Participacion.usuario_id == usuario.id
        ).all()
        
        # Sumar todos los puntos que obtuvo
        puntaje_total = sum(p.puntaje_obtenido for p in participaciones)
        
        ranking_items.append({
            "usuario_id": usuario.id,
            "usuario_nombre": usuario.nombre,
            "puntaje_total": puntaje_total
        })
    
    # Ordenar de mayor a menor puntaje (el que tiene más puntos primero)
    ranking_items.sort(key=lambda x: x["puntaje_total"], reverse=True)
    
    # Agregar la posición en el ranking
    ranking_final = []
    for posicion, item in enumerate(ranking_items, start=1):
        ranking_final.append(RankingItem(
            posicion=posicion,
            usuario_id=item["usuario_id"],
            usuario_nombre=item["usuario_nombre"],
            puntaje_total=item["puntaje_total"]
        ))
    
    return RankingResponse(
        trivia_id=trivia_id,
        trivia_nombre=trivia.nombre,
        ranking=ranking_final
    )

