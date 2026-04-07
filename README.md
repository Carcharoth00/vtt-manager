## VTT MANAGER

Aplicación de escritorio Python para manejar un VTT (Virtual Table Top). Está basado en mi proyecto de fin de curso, en el que estoy desarrollando un VTT, y me pareció buena idea probra a usar esta tecnología como prueba para un posible cambio en el desarrollo.

## Tecnologías
- Python 3.x + Tkinter (interfaz gráfica)
- PostgreSQL 16 (base de datos)
- Docker + Docker Compose (contenedor)
- psycopg2 (driver de conexión)


## Instalación

1. Clona el repositorio:
   git clone https://github.com/Carcharoth00/vtt-manager.git
   cd vtt-manager

2. Instala las dependencias:
   pip install -r requirements.txt

3. Levanta la base de datos (solo la primera vez):
   docker-compose up -d

4. Ejecuta la aplicacion:
   - Doble clic en iniciar.bat
   - O desde terminal: python main.py

NOTA:
>Si ya tenias el contenedor creado sin el schema, debes recrearlo:
>docker-compose down -v
>docker-compose up -d

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

## Explicación de la estructura

Primero se creo el contenedor Docker, llamado vtt_postgres. Para ello primero se creo el archivo docker-compose.yml, que contiene la "receta" para que docker cree el contenedor, dandole las instrucciones básicas para su creación: nombre, usuario, contraseña, el puerto de conexión y lo más importante: el lenguaje que va a usar que en este caso es PostgreSQL.

Se levantó en contenedor y con la imagen, se crea esta base de datos en un contenedor, ahora vacia. Por que lo que se desarrolla schema.sql, que crea la estructura de tablas que va a tener la base de datos. Al ser un VTT, se crean las tablas para los usuarios, las campañas y las distintas subtablas para las diferentes necesidades. Se inyecta este archivo en el contenedor y ahora nuestro docker ya tiene una estructura de tablas con la que trabajar.

Ahora empezamos con el proyecto Python. Primero, database.py, que tiene las dos funciones principales, get_connection que conecta nuestra aplicación con contenedor y execute_query que inyecta las querys de las funciones en la base de datos para hacer las diferentes peticiones, haciendo la vez de "paloma mensajera" entre la aplicación Python y la BBDD.

Despues, creamos la carpeta modelos, que contendrá los métodos CRUD necesarios para trabajar con la BBDD. En este caso por mejor organización y gestión en el futuro, se crea un archivo según los datos con los que vayamos a trabajar: usuarios, campañas y personajes en este caso.

Cada archivo contiene las funciones responsables de crear, leer, modificar y borrar cada una de sus respectivas partes.

Por último, la carpeta GUI con la interfaz gráfica, para que el usuario pueda utilizar cómodamente las diferente funciones. En este caso hay 3 pestañas, una para usuarios, otra para campañas y otra para personajes. Cada una de ellas tiene una sección para crear nuevos y una lista que muestra los que ya están creados.