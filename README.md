# TalaTrivia API

API para gestionar trivias de preguntas relacionadas con recursos humanos.

Esta es mi implementación de la prueba técnica. La API permite crear usuarios, preguntas, trivias y gestionar las participaciones y rankings.

## 🚀 Inicio Rápido

### Con Docker (Recomendado)

```bash
# Construir y ejecutar
docker-compose up --build

# O si quieres ejecutarlo en segundo plano
docker-compose up --build -d
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Documentación interactiva**: http://localhost:8000/docs
- **Documentación alternativa**: http://localhost:8000/redoc

### Desarrollo Local

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
.\venv\Scripts\Activate.ps1

# Activar entorno virtual (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
uvicorn app.main:app --reload
```

## 📋 Funcionalidades

1. ✅ Usuarios - CRUD completo
2. ✅ Preguntas - CRUD completo
3. ✅ Trivias - CRUD completo
4. ✅ Participación - Completo (ver preguntas, responder, calcular puntajes)
5. ✅ Ranking - Completo (ranking por trivia)

## 📝 Endpoints Disponibles

### Usuarios
- `POST /usuarios` - Crear usuario
- `GET /usuarios` - Listar todos los usuarios
- `GET /usuarios/{id}` - Obtener usuario por ID

### Preguntas
- `POST /preguntas` - Crear pregunta
- `GET /preguntas` - Listar todas las preguntas
- `GET /preguntas/{id}` - Obtener pregunta por ID

**Nota:** Las preguntas tienen niveles de dificultad (fácil, medio, difícil) que otorgan diferentes puntajes:
- Fácil: 1 punto
- Medio: 2 puntos
- Difícil: 3 puntos

### Trivias
- `POST /trivias` - Crear trivia (asignar preguntas y usuarios)
- `GET /trivias` - Listar todas las trivias
- `GET /trivias/{id}` - Obtener trivia por ID

### Participación
- `GET /trivias/{trivia_id}/usuario/{usuario_id}/preguntas` - Ver preguntas de una trivia (SIN respuesta correcta ni dificultad)
- `POST /trivias/{trivia_id}/responder` - Responder una pregunta
- `GET /trivias/{trivia_id}/usuario/{usuario_id}/puntaje` - Ver puntaje de un usuario

### Ranking
- `GET /trivias/{trivia_id}/ranking` - Obtener ranking de usuarios (ordenado de mayor a menor puntaje)

## 🧪 Probar la API

Abre http://localhost:8000/docs para ver la documentación interactiva y probar los endpoints.

## 📁 Estructura del Proyecto

```
IMPLEMENTACION PRUEBA TECNICA/
├── app/
│   ├── __init__.py
│   ├── database.py          # Configuración de la base de datos SQLite
│   ├── main.py              # Todos los endpoints de la API
│   ├── models.py            # Modelos de base de datos (SQLAlchemy)
│   └── schemas.py           # Schemas de validación con Pydantic
├── Dockerfile               # Configuración para Docker
├── docker-compose.yml       # Para ejecutar con Docker Compose
├── requirements.txt         # Dependencias de Python
├── .gitignore              # Archivos que no se suben al repo
└── README.md               # Este archivo
```

## 🔧 Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para base de datos
- **SQLite**: Base de datos (archivo local)
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI
- **Docker**: Containerización

## ✅ Requerimientos Implementados

### 1. Usuarios ✅
- Crear usuarios con nombre y email
- Listar usuarios
- Obtener usuario por ID
- Validación de email único

### 2. Preguntas ✅
- Crear preguntas con múltiples opciones
- Una sola respuesta correcta
- Niveles de dificultad (fácil, medio, difícil)
- Puntajes: fácil=1, medio=2, difícil=3

### 3. Trivias ✅
- Crear trivias con nombre y descripción
- Asignar preguntas a trivias
- Asignar usuarios a trivias

### 4. Participación ✅
- Ver preguntas de una trivia asignada (SIN respuesta correcta ni dificultad)
- Responder preguntas
- Validación automática de respuestas
- Cálculo automático de puntajes según dificultad

### 5. Ranking ✅
- Ranking de usuarios por trivia
- Ordenado de mayor a menor puntaje

## 📝 Notas de Implementación

- **Seguridad**: Los jugadores NO ven la respuesta correcta ni la dificultad de las preguntas (como dice el enunciado)
- **Puntajes**: Se calculan automáticamente según la dificultad (fácil=1 punto, medio=2 puntos, difícil=3 puntos)
- **Validaciones**: Implementé las validaciones necesarias (email único, respuestas válidas, etc.)
- **Base de datos**: Usé SQLite porque es simple y se crea automáticamente al iniciar la API

## 🐳 Docker

El proyecto está completamente dockerizado. Para ejecutarlo:

```bash
docker-compose up --build
```

El contenedor expone el puerto 8000 y la base de datos SQLite se crea automáticamente en `/app/tala_trivia.db`.

