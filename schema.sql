-- Extensión para usar UUID como identificadores únicos
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de usuarios
CREATE TABLE usuarios (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre_usuario   VARCHAR(50)  UNIQUE NOT NULL,
    email            VARCHAR(100) UNIQUE NOT NULL,
    contrasena_hash  VARCHAR(255) NOT NULL,
    fecha_registro   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de campañas
CREATE TABLE campanas (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre           VARCHAR(100) NOT NULL,
    estado           VARCHAR(20)  DEFAULT 'activa'
                     CHECK (estado IN ('activa', 'pausada', 'finalizada')),
    descripcion      TEXT,
    notas            TEXT,
    fecha_creacion   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla intermedia: usuarios <-> campañas (con rol)
CREATE TABLE campanas_usuarios (
    campana_id   UUID REFERENCES campanas(id) ON DELETE CASCADE,
    usuario_id   UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    rol          VARCHAR(10) NOT NULL CHECK (rol IN ('master', 'jugador')),
    fecha_union  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (campana_id, usuario_id)
);

-- Tabla de personajes
CREATE TABLE personajes (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campana_id   UUID REFERENCES campanas(id) ON DELETE CASCADE,
    usuario_id   UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    nombre       VARCHAR(100) NOT NULL,
    raza         VARCHAR(50),
    clase        VARCHAR(50),
    nivel        INT DEFAULT 1 CHECK (nivel >= 1),
    experiencia  INT DEFAULT 0 CHECK (experiencia >= 0),
    imagen_ruta  VARCHAR(255),
    notas        TEXT
);

-- Tabla de estadísticas (1 a 1 con personajes)
CREATE TABLE estadisticas (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    personaje_id  UUID UNIQUE REFERENCES personajes(id) ON DELETE CASCADE,
    fuerza        INT DEFAULT 10 CHECK (fuerza BETWEEN 1 AND 30),
    destreza      INT DEFAULT 10 CHECK (destreza BETWEEN 1 AND 30),
    constitucion  INT DEFAULT 10 CHECK (constitucion BETWEEN 1 AND 30),
    inteligencia  INT DEFAULT 10 CHECK (inteligencia BETWEEN 1 AND 30),
    sabiduria     INT DEFAULT 10 CHECK (sabiduria BETWEEN 1 AND 30),
    carisma       INT DEFAULT 10 CHECK (carisma BETWEEN 1 AND 30),
    vida_max      INT DEFAULT 10 CHECK (vida_max >= 1),
    vida_actual   INT DEFAULT 10 CHECK (vida_actual >= 0)
);

-- Tabla de inventario
CREATE TABLE inventario (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    personaje_id    UUID REFERENCES personajes(id) ON DELETE CASCADE,
    nombre_objeto   VARCHAR(100) NOT NULL,
    tipo            VARCHAR(50),
    descripcion     TEXT,
    cantidad        INT DEFAULT 1 CHECK (cantidad >= 0)
);

-- Tabla de mapas
CREATE TABLE mapas (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campana_id    UUID REFERENCES campanas(id) ON DELETE CASCADE,
    nombre        VARCHAR(100) NOT NULL,
    archivo_ruta  VARCHAR(255),
    notas         TEXT
);

-- ============================================
-- DATOS DE EJEMPLO
-- ============================================

-- Usuarios (contraseñas en texto plano: gandalf→"admin", frodo→"1234")
INSERT INTO usuarios (id, nombre_usuario, email, contrasena_hash) VALUES
  ('a0000000-0000-0000-0000-000000000001', 'gandalf', 'gandalf@ejemplo.com', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'),
  ('a0000000-0000-0000-0000-000000000002', 'frodo',   'frodo@ejemplo.com',   '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4');

-- Campañas
INSERT INTO campanas (id, nombre, estado, descripcion) VALUES
  ('b0000000-0000-0000-0000-000000000001', 'La Sombra del Norte', 'activa',   'Una campaña épica en las tierras del norte.'),
  ('b0000000-0000-0000-0000-000000000002', 'El Retorno del Rey',  'pausada',  'La batalla final por la Tierra Media.');

-- Miembros de campaña
INSERT INTO campanas_usuarios (campana_id, usuario_id, rol) VALUES
  ('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'master'),
  ('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000002', 'jugador'),
  ('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000002', 'master'),
  ('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'jugador');

-- Personajes
INSERT INTO personajes (id, campana_id, usuario_id, nombre, raza, clase, nivel, experiencia) VALUES
  ('c0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000002', 'Aragorn',  'Humano', 'Guerrero', 5, 6500),
  ('c0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'Legolas',  'Elfo',   'Arquero',  4, 4200);

-- Estadísticas
INSERT INTO estadisticas (personaje_id, fuerza, destreza, constitucion, inteligencia, sabiduria, carisma, vida_max, vida_actual) VALUES
  ('c0000000-0000-0000-0000-000000000001', 18, 14, 16, 12, 13, 15, 52, 52),
  ('c0000000-0000-0000-0000-000000000002', 12, 20, 12, 14, 16, 17, 38, 30);

-- Inventario
INSERT INTO inventario (personaje_id, nombre_objeto, tipo, descripcion, cantidad) VALUES
  ('c0000000-0000-0000-0000-000000000001', 'Andúril',        'Arma',    'La llama del oeste, espada de los Reyes de Númenor.', 1),
  ('c0000000-0000-0000-0000-000000000001', 'Cota de malla',  'Armadura','Armadura de acero forjada en el norte.', 1),
  ('c0000000-0000-0000-0000-000000000002', 'Arco de Lothlórien', 'Arma', 'Arco élfico de gran precisión.', 1),
  ('c0000000-0000-0000-0000-000000000002', 'Carcaj de flechas', 'Munición','30 flechas élficas.', 30);
