from club_deportivo import ClubDeportivo
import sqlite3


def iniciar_sesion():
    print("\n--- Iniciar Sesión ---")

    while True:
        usuario = input("Usuario (o escribe 'salir' para cancelar): ")
        if usuario.lower() == 'salir':
            print("Inicio de sesión cancelado.")
            return None

        contraseña = input("Contraseña: ")
        conexion = sqlite3.connect('club_deportes.db')
        cursor = conexion.cursor()
        cursor.execute('''
        SELECT usuario FROM usuarios WHERE usuario = ? AND contraseña = ?
        ''', (usuario, contraseña))
        user = cursor.fetchone()
        conexion.close()

        if user:
            print(f"Bienvenido, {usuario}.")
            return usuario
        else:
            print("Usuario o contraseña incorrectos. Inténtelo de nuevo.\n")


def main():
    usuario = iniciar_sesion()
    if usuario:
        club = ClubDeportivo(usuario)
        club.menu_principal()


if __name__ == "__main__":
    main()
