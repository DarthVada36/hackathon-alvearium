<div align="center">

# 🐭 Ratoncito Pérez Digital & Gymkana Interactiva (Alvearium Edition)

Plataforma full‑stack inteligente para experiencias turísticas familiares en Madrid: guía conversacional (IA), gamificación por puntos, gestión de familias y ruta urbana guiada. Complementa y se integra conceptualmente con el proyecto de juego adicional (búsqueda del diente) disponible en: https://github.com/Jab-bee/Busqueda-del-Diente

</div>

---

## 1. 🎯 Visión General

El objetivo del proyecto es ofrecer una experiencia inmersiva y educativa para familias que recorren Madrid acompañadas por el **agente inteligente “Ratoncito Pérez”**. El asistente conversa en lenguaje natural, adapta su tono a los niños, ofrece curiosidades históricas y otorga puntos mágicos según la interacción y el progreso en una **ruta urbana (10 POIs)**. La capa de juego (proyecto complementario: _Búsqueda del Diente_) añade misiones temáticas y retos ampliando la narrativa.

Componentes clave:

- Frontend SPA (React + Vite + Tailwind) con mapa interactivo, chat y panel de progreso.
- Backend API (FastAPI) con autenticación JWT, orquestación del agente y servicios optimizados.
- Persistencia en **PostgreSQL (Supabase)** y soporte para caché / futuro escalado con **Redis**.
- Búsqueda semántica y conocimiento contextual de Madrid mediante **Embeddings + Pinecone + Wikipedia**.
- Sistema de puntos y logros (gamificación) + control de avance en la ruta.
- Arquitectura preparada para incorporar otros modelos (Groq LLM / OpenAI fallback) y enriquecer la capa de juego (proyecto complementario).

## 2. ✨ Características Principales

- IA conversacional contextual adaptada a familias y edades.
- Modelo de interacción optimizado (prompt híbrido + historial reducido + contexto dinámico de lugar).
- Ruta guiada fija de 10 puntos (POIs) con avance explícito / validación simulada.
- Sistema de puntuación (llegada, engagement, curiosidad) con lógica idempotente.
- Gestión de usuarios, familias y miembros (adult/child) con control de propiedad.
- Persistencia de contexto conversacional y progreso por familia.
- Embeddings cacheados (servicio singleton) + integración Pinecone (vector store) + fallback semántico.
- Ingesta de conocimiento desde Wikipedia (resúmenes) con política de User-Agent académica.
- Endpoints de depuración (Pinecone / Redis / Wikipedia / Geocoding) y health checks ampliados.
- Arquitectura escalable orientada a micro‑servicios lógicos (servicios de embeddings, vector DB, autenticación, puntos, conocimiento, ruta, agente).
- Seguridad JWT con expiración configurable y validación de ownership por familia.
- Integración ampliable con sistema de juego paralelo (misiones, coleccionables, “búsqueda del diente”).

## 3. 🗂️ Estructura de Carpetas (Resumen)

```
hackathon-alvearium/
├─ README.md                      # Documentación principal
├─ requirements.txt               # (si aplica global)
├─ Server/                        # Backend FastAPI + Servicios IA
│  ├─ main.py                     # Punto de entrada FastAPI (lifespan orchestrator)
│  ├─ config.py                   # Configuración (Pydantic Settings)
│  ├─ api/
│  │  ├─ endpoints/               # Routers: auth, chat, families, routes, debug
│  │  └─ dependencies.py          # Inyección de dependencias comunes
│  ├─ core/
│  │  ├─ agents/                  # Lógica de dominio del agente
│  │  │  ├─ raton_perez.py        # Orquestador conversacional principal
│  │  │  ├─ madrid_knowledge.py   # Capa de conocimiento + Pinecone + Wikipedia
│  │  │  ├─ family_context.py     # Gestión de memoria / progreso por familia
│  │  │  ├─ points_system.py      # Sistema de puntos y logros
│  │  │  ├─ location_helper.py    # Definición de ruta y POIs
│  │  ├─ models/
│  │  │  ├─ database.py           # Conexión Supabase / PostgreSQL
│  │  │  ├─ schemas.py            # Pydantic Schemas (Auth / Chat / Family)
│  │  ├─ security/                # JWT & dependencias de seguridad
│  │  │  ├─ auth.py               # Hash + emisión/verificación de tokens
│  │  │  ├─ dependencies.py       # `get_current_user` y ownership checks
│  │  ├─ services/                # Servicios reutilizables (infra IA)
│  │  │  ├─ embedding_service.py  # Singleton embeddings + caché
│  │  │  ├─ pinecone_service.py   # Abstracción Pinecone v3
│  │  │  ├─ groq_service.py       # Wrapper LLM (Groq)
│  │  │  ├─ madrid_apis.py        # (extensible para APIs externas)
│  │  ├─ tests/                   # Pruebas (unitarias/integración)
│  └─ requirements.txt            # Dependencias backend
├─ client/                        # Frontend React (Vite)
│  ├─ src/
│  │  ├─ pages/                   # Vistas (Dashboard, ChatBot, Gymkana, etc.)
│  │  ├─ components/              # Componentes reutilizables (Header, Map ...)
│  │  ├─ context/                 # AuthContext (gestión estado auth)
│  │  ├─ services/ApiService.js   # Abstracción de llamadas a la API
│  │  ├─ assets/                  # Imágenes / íconos
│  ├─ package.json                # Dependencias FE
│  ├─ tailwind.config.js          # Config UI
│  └─ vite.config.js              # Configuración bundler
└─ .env.example                   # (Propuesto – ver sección Variables)
```

## 4. 🧱 Arquitectura Lógica

### 4.1 Diagrama de Alto Nivel (ASCII)

```
┌──────────────┐        HTTPS        ┌──────────────────────────┐
│  React SPA   │  ─────────────────▶ │ FastAPI API Gateway      │
│ (Vite+Router)│    JSON (REST)      │ (Routers + Lifespan)     │
└──────┬───────┘                     └──────────┬──────────────┘
       │ CORS / Auth (Bearer JWT)               │
       │                                        │ Orquestación
       ▼                                        ▼
┌──────────────────────────┐        ┌──────────────────────────┐
│  Auth / Families Service │        │  Chat & Agent Orchestr. │
│  (users, families, membres)       │  (raton_perez.py)        │
└──────────┬────────────────        └──────────┬──────────────┘
           │ Persistence (SQL)                 │ Context & Puntos
           ▼                                    ▼
┌──────────────────────────┐        ┌──────────────────────────┐
│ PostgreSQL (Supabase)    │◀──────▶│ Family Context Cache     │
│ (users, families, route) │        │ (mem + persisted)        │
└──────────┬───────────────┘        └──────────┬──────────────┘
           │                                     │
           ▼                                     ▼
   (Opcional Redis)                      ┌──────────────────────┐
                                         │ EmbeddingService     │
                                         │ (Singleton + Cache)  │
                                         └─────────┬───────────┘
                                                   ▼
                                           ┌───────────────────┐
                                           │ Pinecone Vector DB │
                                           └─────────┬─────────┘
                                                     ▼ (Fallback / Online fetch)
                                           ┌──────────────────────────┐
                                           │ Wikipedia REST (Resumen) │
                                           └──────────────────────────┘
```

### 4.2 Flujo de un Mensaje de Chat

1. Usuario envía texto desde `ChatBot.jsx` → `ApiService.sendChatMessage`.
2. Backend: `/api/chat/message` valida JWT + ownership de la familia.
3. Se carga (o inicializa) el `FamilyContext` (memoria + progreso + visited_pois).
4. Se analiza la “situación” (pregunta sobre lugar, conversación general, etc.).
5. Se computan puntos (`points_system.evaluate_points`).
6. Se construye prompt contextual (familia + situación + conocimiento dinámico).
7. `groq_service` genera respuesta (LLM) con fallback degradado si falta vector store.
8. Se actualiza contexto (historial, puntos, visited_pois) y se persiste.
9. Se responde JSON al frontend (respuesta, puntos, logros, situación).

## 5. 🧩 Capa de Conocimiento y Búsqueda Semántica

| Componente          | Función                                                  | Optimizaciones                                 |
| ------------------- | -------------------------------------------------------- | ---------------------------------------------- |
| `embedding_service` | Generación de embeddings e5 (cache en memoria)           | Singleton + warm‑up + cache MD5                |
| `pinecone_service`  | Indexación y búsqueda vectorial de textos Wikipedia/POIs | Cache local de vectores, batch existence check |
| `madrid_knowledge`  | Orquesta extracción Wikipedia + inserción condicional    | Evita reprocesar vectores existentes           |
| Fallback keywords   | Respuestas aproximadas sin Pinecone                      | Garantiza continuidad                          |

## 6. 🔐 Seguridad

- Autenticación: JWT (HS256) – emisión al registrar / login.
- Middleware: dependencia `get_current_user` + verificación de propiedad (`require_family_ownership`).
- Expiración configurable (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- Recomendación: rotar `SECRET_KEY` en producción y usar HTTPS / proxy inverso.

## 7. 📦 Tecnologías y Dependencias Clave

### Backend

- Python 3.10+/FastAPI, Uvicorn
- Pydantic / pydantic-settings
- psycopg2 + Supabase Python SDK
- jose (JWT), passlib (bcrypt)
- langchain, langchain_groq
- sentence-transformers (embeddings)
- pinecone (SDK v3)
- requests

### Frontend

- React 19 + Vite 7
- React Router DOM v7
- TailwindCSS 3, Lucide Icons, React Icons
- Leaflet + react-leaflet (mapa) + leaflet-routing-machine (extensible)

### Infra / Otros

- PostgreSQL (Supabase managed)
- (Opcional) Redis para cache de sesiones/eventos futuros
- Wikipedia REST API, Eventbrite (eventos), Google Places (opcional)

## 8. ⚙️ Variables de Entorno (.env)

Crear `.env` en la raíz del backend (o usar `.env` global) con al menos:

```
# === Core Backend ===
SECRET_KEY=changeme_super_secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# === Supabase / PostgreSQL ===
SUPABASE_URL=...
SUPABASE_PUBLIC_KEY=...
SUPABASE_SERVICE_ROLE=postgresql_connection_string  # Para psycopg2 directo

# === Groq / LLM ===
GROQ_API_KEY=...

# === Pinecone / Vector Store ===
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=perez
PINECONE_DIMENSION=1024
PINECONE_METRIC=cosine
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_EMBEDDING_MODEL=intfloat/e5-large-v2

# === (Opcional) Otros ===
OPENAI_API_KEY=...
REDIS_URL=redis://localhost:6379/0
EVENTBRITE_TOKEN=...
GOOGLE_API_KEY=...
MADRID_API_KEY=...
```

## 9. 🛠️ Instalación (Desarrollo – Windows / Bash)

### 9.1 Prerrequisitos

- Python 3.10+ / Node.js 20+
- (Opcional) Docker (para Redis)
- Cuenta Supabase + Pinecone + Groq API Key

### 9.2 Backend

```bash
python -m venv .venv
source .venv/Scripts/activate  # o .venv/bin/activate según shell
pip install --upgrade pip
pip install -r Server/requirements.txt
cp .env.example .env  # (si has creado el ejemplo)
python -m uvicorn Server.main:app --reload
```

Accede a: http://localhost:8000/docs

### 9.3 Frontend

```bash
cd client
npm install
npm run dev
```

Accede a: http://localhost:5173

### 9.4 (Opcional) Redis vía Docker

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

## 10. 🚀 Uso Rápido (Flujo Principal)

1. Registrar usuario: `POST /api/auth/register` → guardar `access_token`.
2. Crear familia: `POST /api/families/` con miembros (adult/child).
3. Obtener overview de ruta: `GET /api/routes/overview`.
4. Enviar primer mensaje de chat: `POST /api/chat/message`.
5. Avanzar al siguiente POI: `POST /api/routes/family/{id}/advance`.
6. Consultar estado: `GET /api/chat/family/{id}/status`.

## 11. 📡 Endpoints (Resumen + Ejemplos)

### 11.1 Autenticación (`/api/auth`)

| Método | Endpoint              | Descripción                        |
| ------ | --------------------- | ---------------------------------- |
| POST   | /register             | Registro (email, password, avatar) |
| POST   | /login                | Login (JWT)                        |
| GET    | /me                   | Perfil + familias + estadísticas   |
| POST   | /logout               | Lógico (frontend borra token)      |
| PUT    | /profile?avatar=icon2 | Actualiza avatar                   |

Ejemplo Registro:

```json
POST /api/auth/register
{
  "email": "familia@example.com",
  "password": "segura123",
  "avatar": "icon1"
}
→ 200 {"access_token": "...", "user": {"id":1, "email":"..."}}
```

### 11.2 Familias (`/api/families`)

| Método | Endpoint     | Descripción                |
| ------ | ------------ | -------------------------- |
| POST   | /            | Crea familia + miembros    |
| GET    | /            | Lista familias del usuario |
| GET    | /{family_id} | Detalle familia            |
| DELETE | /{family_id} | Elimina familia            |

Payload creación:

```json
{
  "name": "Los Exploradores",
  "preferred_language": "es",
  "members": [
    { "name": "Ana", "age": 38, "member_type": "adult" },
    { "name": "Luis", "age": 8, "member_type": "child" }
  ]
}
```

### 11.3 Chat (`/api/chat`)

| Método | Endpoint                      | Descripción                    |
| ------ | ----------------------------- | ------------------------------ |
| POST   | /message                      | Envía mensaje al agente        |
| GET    | /family/{id}/status           | Estado puntos / progreso       |
| GET    | /family/{id}/history?limit=20 | Historial reciente             |
| DELETE | /family/{id}/history          | Limpia conversación            |
| GET    | /families                     | Familias disponibles para chat |

Ejemplo Mensaje:

```json
POST /api/chat/message
{
  "family_id": 1,
  "message": "¿Qué puedes contarme del Palacio Real?"
}
→ {
  "success": true,
  "response": "El Palacio Real...",
  "points_earned": 75,
  "total_points": 175,
  "situation": "location_question",
  "achievements": ["poi_engagement"]
}
```

### 11.4 Ruta / Progreso (`/api/routes`)

| Método | Endpoint             | Descripción                             |
| ------ | -------------------- | --------------------------------------- |
| GET    | /family/{id}/next    | Informa próximo POI (con info dinámica) |
| POST   | /family/{id}/advance | Avanzar (otorga puntos llegada)         |
| GET    | /overview            | Lista estática de POIs                  |
| POST   | /location/update     | Simula actualización ubicación          |

### 11.5 Debug / Health

| Endpoint                            | Descripción                              |
| ----------------------------------- | ---------------------------------------- |
| GET /health                         | Estado general (db + embeddings)         |
| GET /healthz                        | Estado extendido (auth, pinecone, redis) |
| GET /api/stats/services             | Stats caches                             |
| GET /debug/pinecone                 | Estado Pinecone                          |
| GET /debug/wiki?title=Plaza%20Mayor | Test Wikipedia                           |
| GET /\_routes                       | Inventario rutas (debug)                 |

## 12. 🧮 Modelo de Datos (Esquema Simplificado)

| Tabla                 | Campos Principales                                                           | Notas                        |
| --------------------- | ---------------------------------------------------------------------------- | ---------------------------- |
| users                 | id, email (uniq), hashed_password, avatar, created_at, last_login, is_active | JWT `sub` = id               |
| families              | id, user_id(FK), name, preferred_language, conversation_context(jsonb)       | 1:N users→families           |
| family_members        | id, family_id(FK), name, age, member_type                                    | member_type ∈ {adult, child} |
| family_route_progress | id, family_id(FK), current_poi_index, points_earned, current_location(json)  | Actualiza en cada avance     |

`conversation_context` persiste: memory[], visited_pois[], speaker, updated_at.

## 13. 🏆 Sistema de Puntos

| Evento                           | Puntos | Condición                            |
| -------------------------------- | ------ | ------------------------------------ |
| Llegada a POI                    | 100    | Primera vez (idempotente)            |
| Engagement (pregunta contextual) | 75     | Solo una vez por POI                 |
| Extra fallback                   | 5      | Curiosidad sin categoría (degradado) |

Gestión idempotente vía flags en `visited_pois[].points_awarded`.

## 14. 🧪 Pruebas

- Ubicadas en `Server/core/tests` (nomenclatura `test_*.py`).
- Ejecutar:

```bash
pytest -q
```

- Recomendado: generar datos de prueba (fixtures) o usar una base temporal.

## 15. 🔄 Estrategia de Branching / Contribución

1. `main` / `stable` – producción.
2. `develop` (si se adopta) – integración continua.
3. `feature/<nombre>` – nuevas funcionalidades.
4. Convenciones commits (recomendado):
   - `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
5. Flujo PR:
   - Crear rama → desarrollar → pruebas locales → abrir PR con descripción técnica + capturas (si UI).
   - Revisión (>=1 aprobaciones) → merge squash (limpieza historial).
6. Estándares Código Backend:
   - Tipado Pydantic / evitar lógica en routers (delegar a servicios).
   - Logs claros (nivel INFO / WARNING / ERROR).
   - Funciones ≤ 60 líneas preferentemente.

## 16. 🔐 Recomendaciones Producción

- Servir detrás de reverse proxy (Nginx / Traefik) + HTTPS.
- Activar rate limiting (API Gateway externo o plugin FastAPI).
- Rotación de claves y secretos (Vault / Doppler / AWS Secrets Manager).
- Monitorización: Prometheus exporter + dashboards (p.ej. latencias de `/api/chat/message`).
- Pruebas de carga en endpoints críticos (chat, advance route).
- Pre‑carga de embeddings / warm-up en startup controlado.

## 17. 🧩 Integración con Proyecto “Búsqueda del Diente”

El repositorio complementario expande la narrativa añadiendo retos específicos (misiones coleccionables). Puntos de integración sugeridos:

- Reutilizar `family_id` como clave de sesión lúdica.
- Mapear logros adicionales a `achievements` retornados por `/api/chat/message`.
- Extender `family_route_progress` con campos de coleccionables (JSONB: `game_state`).
- Añadir endpoint `/api/game/quests` (futuro) sincronizando estados con el otro proyecto.

## 18. 🗺️ Roadmap Futuro (Propuesto)

- [ ] Streaming de respuestas (Server-Sent Events / WebSocket).
- [ ] Geofencing real (validación GPS para otorgar llegada).
- [ ] Modo offline PWA con cache de últimos POIs.
- [ ] Panel administrativo (moderación / métricas de uso).
- [ ] Internacionalización completa (i18n FE + prompts multilingües).
- [ ] Integración de misiones del juego complementario vía micro-servicio.

## 19. 📄 Licencia

Actualmente sin licencia explícita. Se recomienda MIT:

```
MIT License (propuesta)
Copyright (c) 2025 Contributors
Permission is hereby granted, free of charge, to any person obtaining a copy ...
```

Añadir `LICENSE` definitivo antes de distribución pública.

## 20. 👥 Autores y Equipo

| Nombre (GitHub) | Email                        |
| --------------- | ---------------------------- |
| Jab-bee         | oneprueba123@gmail.com       |
| a-bac-0         | anca.bacria@thevallians.com  |
| JIMENA-ft       | floresticonajimena@gmail.com |
| peperuizdev     | jorsqn@gmail.com             |
| mariasuescum    | andreinasuescum@gmail.com    |
| DarthVada36     | velazquezvada@gmail.com      |

Colaboraciones futuras: abrir PR o crear issue con etiqueta `enhancement`.

## 21. ❗ Notas y Limitaciones Conocidas

- Validación de ubicación aún simulada (no geofencing real).
- Falta limpieza periódica de contexto histórico (retención limitada en memoria).
- Sin invalidación activa de JWT (logout stateless).
- Reintentos limitados en ingestión de Wikipedia (tolerancia a fallos básica).

## 22. 🧾 Ejemplo de Interacción (Secuencia Simplificada)

```
Cliente → POST /api/auth/register
Cliente → POST /api/families/ (crea familia #1)
Cliente → POST /api/chat/message {family_id:1, "Hola"}
Servidor → Analiza situación ⇒ general_conversation
Servidor → LLM genera respuesta + 0 puntos
Cliente → POST /api/routes/family/1/advance  (llega al siguiente POI) ⇒ +100
Cliente → POST /api/chat/message "¿Qué es este lugar?" ⇒ +75 engagement
```

## 23. 🛡️ Calidad y Observabilidad (Sugerido)

- Añadir métricas: tiempo respuesta chat, tasa fallos LLM, aciertos cache embeddings.
- Logging estructurado (JSON) para correlación.
- Trazas distribuidas (OpenTelemetry) en futuro si se separa en microservicios.

---

**Fin del Documento** – Para dudas técnicas abrir issue o contactar a los autores.
