#VTT MANAGER

Aplicación de escritorio Python para manejar un VTT (Virtual Table Top). Está basado en mi proyecto de fin de curso, en el que estoy desarrollando un VTT, y me pareció buena idea probra a usar esta tecnología como prueba para un posible cambio en el desarrollo.

## Tecnologías
- Python 3.x + Tkinter (interfaz gráfica)
- PostgreSQL 16 (base de datos)
- Docker + Docker Compose (contenedor)
- psycopg2 (driver de conexión)


## Instalación

1. Clona el repositorio:
   git clone https://github.com/tu-usuario/vtt-manager.git
   cd vtt-manager

2. Instala las dependencias:
   pip install psycopg2-binary pillow

3. Levanta la base de datos:
   docker-compose up -d

4. Crea las tablas:
   docker cp schema.sql vtt_postgres:/schema.sql
   docker exec -it vtt_postgres psql -U vtt_admin -d vtt_database -f /schema.sql

5. Ejecuta la aplicación:
   python main.py

## Estructura del proyecto
vtt-manager/
├── app/
│   ├── database.py          # Conexión y queries a PostgreSQL
│   ├── modelos/
│   │   ├── usuarios.py      # CRUD de usuarios
│   │   ├── campanas.py      # CRUD de campañas
│   │   └── personajes.py    # CRUD de personajes y estadísticas
│   └── gui/
│       └── ventana_principal.py  # Interfaz gráfica con Tkinter
├── docker-compose.yml       # Configuración del contenedor PostgreSQL
├── schema.sql               # Esquema de la base de datos
└── main.py                  # Punto de entrada