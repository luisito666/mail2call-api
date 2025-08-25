# MailToCall API

API REST para el sistema MailToCall que gestiona grupos de contactos, triggers, contactos, logs de llamadas y eventos de email.

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido para construir APIs con Python
- **AsyncPG**: Cliente PostgreSQL asíncrono
- **Pydantic**: Validación de datos usando type hints de Python
- **Python-Jose**: Manejo de tokens JWT para autenticación
- **Passlib**: Hashing seguro de contraseñas con bcrypt
- **Uvicorn**: Servidor ASGI de alto rendimiento

## Estructura del Proyecto

```
app/
├── api/                    # Endpoints de la API
│   ├── auth.py            # Autenticación y autorización
│   ├── call_logs.py       # Gestión de logs de llamadas
│   ├── contact_groups.py  # Gestión de grupos de contactos
│   ├── contacts.py        # Gestión de contactos
│   ├── email_events.py    # Gestión de eventos de email
│   ├── system_stats.py    # Estadísticas del sistema
│   └── triggers.py        # Gestión de triggers
├── core/                  # Configuración y utilidades centrales
│   ├── auth.py           # Lógica de autenticación
│   └── config.py         # Configuración de la aplicación
├── crud/                  # Operaciones CRUD
├── database/              # Conexión a base de datos
│   └── connection.py
├── schemas/               # Modelos Pydantic para validación
└── main.py               # Aplicación principal FastAPI
```

## Instalación y Configuración

### Requisitos Previos

- Python 3.11+
- PostgreSQL
- Docker (opcional)

### Instalación Local

1. Clona el repositorio:
```bash
git clone <repository-url>
cd mailtocall-api
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las variables de entorno creando un archivo `.env`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/mailtocall
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Ejecuta la aplicación:
```bash
python run.py
```

### Instalación con Docker

1. Ejecuta con Docker Compose:
```bash
docker-compose up --build
```

La API estará disponible en `http://localhost:8000`

## Endpoints de la API

La API incluye endpoints para:

- **Autenticación**: Login y gestión de tokens JWT
- **Grupos de Contactos**: CRUD de grupos de contactos
- **Contactos**: Gestión de contactos individuales
- **Triggers**: Configuración de triggers de email
- **Logs de Llamadas**: Registro y consulta de llamadas realizadas
- **Eventos de Email**: Seguimiento de eventos de email
- **Estadísticas del Sistema**: Métricas y estadísticas generales

## Documentación de la API

Una vez ejecutándose la aplicación, la documentación interactiva está disponible en:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Endpoints de Salud

- `GET /`: Mensaje de bienvenida
- `GET /health`: Check de salud de la aplicación

## Desarrollo

### Estructura de Desarrollo

- Los endpoints de la API están organizados por funcionalidad en el directorio `app/api/`
- Los esquemas de validación están en `app/schemas/`
- Las operaciones CRUD están en `app/crud/`
- La configuración central está en `app/core/`

### Características de Seguridad

- Autenticación JWT
- Hashing seguro de contraseñas con bcrypt
- Validación de datos con Pydantic
- CORS configurado (ajustar para producción)

## Licencia

[Especificar licencia del proyecto]