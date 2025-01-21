# config_db.py
import sqlite3


def crear_tablas(cursor):

    # Crear tabla de roles
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    )
    ''')

    # Crear tabla de permisos para los roles
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS permisos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rol_id INTEGER,
        gestion_profesores INTEGER DEFAULT 0,
        menu_deportes INTEGER DEFAULT 0,
        gestion_cuotas_y_socios INTEGER DEFAULT 0,
        rendicion_cuentas INTEGER DEFAULT 0,
        FOREIGN KEY (rol_id) REFERENCES roles(id)
    )
    ''')

    # Crear tabla de usuarios con rol y contraseña hasheada
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        usuario TEXT PRIMARY KEY,
        contraseña TEXT NOT NULL,
        rol_id INTEGER,
        FOREIGN KEY (rol_id) REFERENCES roles(id)
    )
    ''')

    # Crear tabla de socios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS socios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        domicilio TEXT,
        telefono TEXT,
        email TEXT,
        fecha_inscripcion DATE,
        cuota_social REAL DEFAULT 0,
        fecha_vencimiento DATE
    )
    ''')

    # Crear tabla de no_socios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS no_socios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        telefono TEXT,
        email TEXT
    )
    ''')

    # Crear tabla de invitados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invitados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        dni TEXT NOT NULL,
        socio_dni TEXT NOT NULL,
        FOREIGN KEY(socio_dni) REFERENCES socios(dni)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rendicion_cuentas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni TEXT NOT NULL,
        monto REAL NOT NULL,
        tipo_pago TEXT NOT NULL,
        metodo_pago TEXT NOT NULL,
        fecha_pago DATE NOT NULL,
        tipo_persona TEXT NOT NULL,
        fecha_vencimiento DATE

    )
    ''')

    # tabla de profesores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS profesores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        telefono TEXT,
        domicilio TEXT,
        fecha_ingreso DATE,
        deporte TEXT
    )
    ''')

    # tabla de deportes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS deportes (
        nombre TEXT PRIMARY KEY,
        dias TEXT,
        horarios TEXT,
        profesor TEXT,
        cupos INTEGER DEFAULT 0,
        cuota REAL DEFAULT 0
    )
    ''')

    # tabla de inscripciones

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inscripciones (
        dni_socio TEXT,
        nombre INTEGER,
        cuota INTEGER,
        FOREIGN KEY (dni_socio) REFERENCES socios (dni),
        FOREIGN KEY (nombre) REFERENCES deportes(nombre)
    )
    ''')


def insertar_datos_iniciales(cursor):
    # Insertar roles si no existen
    cursor.execute(
        "INSERT OR IGNORE INTO roles (nombre) VALUES ('Administrador')")
    cursor.execute("INSERT OR IGNORE INTO roles (nombre) VALUES ('Contador')")
    cursor.execute(
        "INSERT OR IGNORE INTO roles (nombre) VALUES ('Recepcionista')")

    # Insertar permisos iniciales para cada rol
    cursor.execute('''
    INSERT OR IGNORE INTO permisos (rol_id, gestion_profesores, menu_deportes, gestion_cuotas_y_socios, rendicion_cuentas)
    VALUES 
        (1, 1, 1, 1, 1),  -- Administrador: acceso completo
        (2, 0, 0, 0, 1),  -- Contador: acceso a Rendición de Cuentas y Salir
        (3, 0, 0, 1, 0)   -- Recepcionista: acceso a Gestionar Cuotas y Socios y Salir.
    ''')

    # Insertar usuarios de ejemplo sin hashing de contraseñas
    cursor.execute(''' 
    INSERT OR IGNORE INTO usuarios (usuario, contraseña, rol_id) 
    VALUES 
        ('admin', 'admin123', 1), 
        ('contador', 'contador123', 2), 
        ('recepcionista', 'recep123', 3)
    ''')


def inicializar_base_datos():
    conexion = sqlite3.connect('club_deportes.db')
    cursor = conexion.cursor()
    crear_tablas(cursor)
    insertar_datos_iniciales(cursor)
    conexion.commit()
    conexion.close()
    print("Base de datos inicializada con éxito.")


if __name__ == "__main__":
    inicializar_base_datos()
