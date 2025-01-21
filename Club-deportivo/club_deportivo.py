import sqlite3
from datetime import datetime, timedelta
import re


class ClubDeportivo:
    def __init__(self, usuario):
        self.usuario = usuario
        self.rol = self.obtener_rol_usuario()
        self.deportes = {
            "Futbol": {"dias": "", "horarios": "", "profesor": "", "cupos": 0, "cuota": 0.0, "inscritos": []},
            "Tenis": {"dias": "", "horarios": "", "profesor": "", "cupos": 0, "cuota": 0.0, "inscritos": []},
            "Natacion": {"dias": "", "horarios": "", "profesor": "", "cupos": 0, "cuota": 0.0, "inscritos": []}
        }

    def conectar_db(self):
        try:
            return sqlite3.connect('club_deportes.db')
        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
            return None

    def obtener_rol_usuario(self):
        with self.conectar_db() as conexion:
            cursor = conexion.cursor()
            cursor.execute('''
                SELECT roles.nombre
                FROM usuarios
                JOIN roles ON usuarios.rol_id = roles.id
                WHERE usuarios.usuario = ?
            ''', (self.usuario,))
            rol = cursor.fetchone()
            return rol[0] if rol else None

    def menu_principal(self):
        while True:
            print("\n--- Menú Principal ---")
            print("1. Gestionar Profesores")
            print("2. Deportes")
            print("3. Gestionar Cuotas y Socios")
            print("4. Rendición de Cuentas")
            print("5. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == "1" and self.tiene_permiso("gestion_profesores"):
                self.gestion_profesores()
            elif opcion == "2" and self.tiene_permiso("menu_deportes"):
                self.menu_deportes()
            elif opcion == "3" and self.tiene_permiso("gestion_cuotas_y_socios"):
                self.gestion_cuotas_y_socios()
            elif opcion == "4" and self.tiene_permiso("rendicion_cuentas"):
                self.rendir_cuentas()
            elif opcion == "5":
                print("Saliendo...")
                break
            else:
                print("Opción no válida o permiso insuficiente.")

    def tiene_permiso(self, permiso):
        with self.conectar_db() as conexion:
            cursor = conexion.cursor()
            cursor.execute('''
            SELECT permisos.{}
            FROM permisos
            JOIN usuarios ON permisos.rol_id = usuarios.rol_id
            WHERE usuarios.usuario = ?
        '''.format(permiso), (self.usuario,))
        permiso_otorgado = cursor.fetchone()
        return permiso_otorgado[0] == 1 if permiso_otorgado else False

    def gestion_profesores(self):
        while True:
            print("\n--- Gestión de Profesores ---")
            print("1. Agregar Profesor")
            print("2. Eliminar Profesor")
            print("3. Lista de Profesores")
            print("4. Volver")
            opcion = input("Seleccione una opción: ")
            if opcion == '1':
                self.agregar_profesor()
            elif opcion == '2':
                self.eliminar_profesor()
            elif opcion == '3':
                self.listar_profesores()
            elif opcion == '4':
                break
            else:
                print("Opción inválida, intente nuevamente.")

    def agregar_profesor(self):
        try:
            # Validar el DNI
            dni = input("DNI del profesor: ")
            if not dni.isdigit() or len(dni) != 8:  # Asumiendo un DNI de 8 dígitos numéricos
                print("Error: El DNI debe ser un número de 8 dígitos.")
                return

            # Validar el nombre (permitir tildes y caracteres especiales)
            nombre = input("Nombre: ").strip().capitalize()
            if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", nombre) or len(nombre) < 2:
                print(
                    "Error: El nombre debe contener solo letras (incluyendo tildes y ñ) y tener al menos 2 caracteres.")
                return

            # Validar el apellido
            apellido = input("Apellido: ").strip().capitalize()
            if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", apellido) or len(apellido) < 2:
                print(
                    "Error: El apellido debe contener solo letras (incluyendo tildes y ñ) y tener al menos 2 caracteres.")
                return

            # Validar teléfono
            telefono = input("Teléfono: ")
            if not telefono.isdigit() or len(telefono) < 7:
                print(
                    "Error: El teléfono debe ser un número válido de al menos 7 dígitos.")
                return

            # Validar domicilio
            domicilio = input("Domicilio: ")
            if len(domicilio) < 5:
                print("Error: El domicilio debe tener al menos 5 caracteres.")
                return

            # Validar la fecha de ingreso
            fecha_ingreso = input("Fecha de ingreso (dd/mm/yyyy): ")
            try:
                fecha_ingreso_dt = datetime.strptime(
                    fecha_ingreso, "%d/%m/%Y").date()
            except ValueError:
                print(
                    "Error: El formato de la fecha de ingreso es incorrecto. Debe ser dd/mm/yyyy.")
                return

            # Validar el deporte
            deporte = input("Deporte (Futbol, Tenis, Natacion): ").capitalize()
            if deporte not in ["Futbol", "Tenis", "Natacion"]:
                print("Error: El deporte debe ser Futbol, Tenis o Natacion.")
                return

            # Inserta el nuevo profesor en la base de datos
            with self.conectar_db() as conexion:
                cursor = conexion.cursor()
                cursor.execute('''
                    INSERT INTO profesores (dni, nombre, apellido, telefono, domicilio, fecha_ingreso, deporte)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (dni, nombre, apellido, telefono, domicilio, fecha_ingreso_dt, deporte))

                conexion.commit()
                print("Profesor agregado exitosamente.")

        except sqlite3.IntegrityError:
            print("Error: Ya existe un profesor con ese DNI.")
        except Exception as e:
            print(f"Error al agregar profesor: {e}")

    def eliminar_profesor(self):
        dni = input("DNI del profesor a eliminar: ")
        with self.conectar_db() as conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM profesores WHERE dni=?", (dni,))

                if cursor.rowcount > 0:
                    print("Profesor eliminado exitosamente.")
                else:
                    print("No se encontró ningún profesor con ese DNI.")

                conexion.commit()

            except Exception as e:
                print(f"Error al eliminar profesor: {e}")

    def listar_profesores(self):
        try:
            with self.conectar_db() as conexion:
                # Crear un cursor a partir de la conexión
                cursor = conexion.cursor()

                # Ejecutar la consulta
                cursor.execute(
                    "SELECT dni, nombre, apellido, telefono, domicilio, fecha_ingreso, deporte FROM profesores")
                profesores = cursor.fetchall()

                if profesores:
                    print("\n--- Lista de Profesores ---")
                    for profesor in profesores:
                        print(f"DNI: {profesor[0]}, Nombre: {profesor[1]} {profesor[2]}, Teléfono: {profesor[3]}, "
                              f"Domicilio: {profesor[4]}, Fecha de ingreso: {profesor[5]}, Deporte: {profesor[6]}")
                else:
                    print("No hay profesores registrados.")
        except Exception as e:
            print(f"Error al listar los profesores: {e}")

    def menu_deportes(self):
        while True:
            print("\n--- Menú de Deportes ---")
            print("1. Configurar Deportes")
            print("2. Listar Deportes")
            print("3. Volver")
            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                self.configurar_deportes()
            elif opcion == '2':
                self.listar_deportes()
            elif opcion == '3':
                break
            else:
                print("Opción inválida, intente nuevamente.")

    def configurar_deportes(self):
        while True:
            print("\n--- Configurar Deportes ---")
            deporte = input(
                "Seleccione el deporte a configurar (Futbol, Tenis, Natacion) o 'Salir' para volver: ").capitalize()

            if deporte.lower() == 'salir':
                break
            elif deporte in self.deportes:
                try:
                    # Validar y capturar días y horarios
                    dias = input("Días: ").strip()
                    if not dias:
                        raise ValueError("Los días no pueden estar vacíos.")

                    horarios = input("Horarios: ").strip()
                    if not horarios:
                        raise ValueError(
                            "Los horarios no pueden estar vacíos.")

                    # Validar y capturar nombre del profesor
                    profesor = input(
                        "Nombre y apellido del profesor: ").strip()
                    if not profesor:
                        raise ValueError(
                            "El nombre del profesor no puede estar vacío.")

                    # Validar y capturar cupos
                    try:
                        cupos = int(input("Cupos máximos: "))
                        if cupos <= 0:
                            raise ValueError(
                                "Los cupos deben ser un número entero positivo.")
                    except ValueError:
                        print(
                            "Error: Ingrese un número entero válido para los cupos.")
                        continue

                    # Validar y capturar cuota deportiva
                    try:
                        cuota = float(
                            input(f"Cuota deportiva para {deporte}: "))
                        if cuota < 0:
                            raise ValueError(
                                "La cuota debe ser un número positivo.")
                    except ValueError:
                        print(
                            "Error: Ingrese un valor numérico válido para la cuota.")
                        continue

                    # Actualizar en la base de datos
                    try:
                        with self.conectar_db() as conexion:

                            if conexion is None:
                                print(
                                    "No se pudo establecer la conexión a la base de datos.")
                                return

                            cursor = conexion.cursor()

                            cursor.execute('''
                                INSERT INTO deportes (nombre, dias, horarios, profesor, cupos, cuota)
                                VALUES (?, ?, ?, ?, ?, ?)
                                ON CONFLICT(nombre)
                                DO UPDATE SET dias=?, horarios=?, profesor=?, cupos=?, cuota=?
                            ''', (deporte, dias, horarios, profesor, cupos, cuota, dias, horarios, profesor, cupos, cuota))

                            conexion.commit()
                            print(
                                f"{deporte} configurado exitosamente en la base de datos.")

                    except Exception as e:
                        print(
                            f"Error al configurar deporte en la base de datos: {e}")

                    # Actualizar datos en el sistema
                    self.deportes[deporte] = {
                        'dias': dias,
                        'horarios': horarios,
                        'profesor': profesor,
                        'cupos': cupos,
                        'cuota': cuota
                    }

                except ValueError as ve:
                    print(f"Entrada inválida: {ve}")

            else:
                print("Deporte no válido. Intente nuevamente.")

    def listar_deportes(self):
        try:
            with self.conectar_db() as conexion:
                if conexion is None:
                    print("No se pudo establecer la conexión a la base de datos.")
                    return

                cursor = conexion.cursor()
                cursor.execute(
                    "SELECT nombre, dias, horarios, profesor, cupos, cuota FROM deportes")
                deportes = cursor.fetchall()

                if not deportes:
                    print("No hay deportes configurados.")
                    return

                for deporte in deportes:
                    nombre, dias, horarios, profesor, cupos, cuota = deporte
                    print(f"\nDeporte: {nombre}\nDías: {dias}\nHorarios: {
                        horarios}\nProfesor: {profesor}\nCupos: {cupos}\nCuota: {cuota}")

                    # Obtener los inscritos para el deporte actual
                    cursor.execute(
                        "SELECT dni_socio FROM inscripciones WHERE nombre = ?", (nombre,))
                    inscritos = cursor.fetchall()

                    if inscritos:
                        print("Inscritos:")
                        for inscrito in inscritos:
                            print(f"  DNI del inscrito: {inscrito[0]}")
                    else:
                        print("  No hay inscritos.")

        except Exception as e:
            print(f"Error al listar los deportes: {e}")

    def gestion_cuotas_y_socios(self):
        while True:
            print("\n--- Gestión de Cuotas y Socios ---")
            print("1. Gestionar Socio")
            print("2. Gestionar Invitado")
            print("3. gestionar No Socio")
            print("4. Pagar Cuota Deportiva")
            print("5. Listar Deportes")
            print("6. Volver")
            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                self.gestionar_socios()
            elif opcion == '2':
                self.gestionar_invitados()
            elif opcion == '3':
                self.gestionar_no_socios()
            elif opcion == '4':
                self.pagar_cuota_deportiva()
            elif opcion == '5':
                self.listar_deportes()
            elif opcion == '6':
                print("Saliendo del menú de gestión de cuotas y socios...")
                break
            else:
                print("Opción inválida, intente nuevamente.")

    def gestionar_socios(self):
        while True:
            print("\n--- Gestión de Socios ---")
            print("1. Registrar Socio")
            print("2. Modificar Socio")
            print("3. Eliminar Socio")
            print("4. Listar Socios")
            print("5. Volver")
            opcion = input("Seleccione una opcion: ")

            if opcion == '1':
                self.registrar_socio()
            elif opcion == '2':
                self.modificar_socio()
            elif opcion == '3':
                self.eliminar_socio()
            elif opcion == '4':
                self.listar_socios()
            elif opcion == '5':
                print("Saliendo del menú de gestión de socios...")
                break

    def registrar_socio(self):
        try:
            dni = input("DNI del socio: ").strip()
            if not dni.isdigit() or len(dni) < 7 or len(dni) > 8:
                print("Error: El DNI debe ser un número de 7 u 8 dígitos.")
                return
        # Validar el nombre (permitir tildes y caracteres especiales)
            nombre = input("Nombre: ").strip().capitalize()
            if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", nombre) or len(nombre) < 2:
                print(
                    "Error: El nombre debe contener solo letras (incluyendo tildes y ñ) y tener al menos 2 caracteres.")
                return

            # Validar el apellido
            apellido = input("Apellido: ").strip().capitalize()
            if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", apellido) or len(apellido) < 2:
                print(
                    "Error: El apellido debe contener solo letras (incluyendo tildes y ñ) y tener al menos 2 caracteres.")
                return
            domicilio = input("Domicilio: ").strip().capitalize()
            telefono = input("Teléfono: ").strip()
            if not domicilio or not telefono.isdigit():
                print(
                    "Error: El domicilio no puede estar vacío y el teléfono debe contener solo números.")
                return
            email = input("Email: ").strip()
            if "@" not in email or "." not in email.split("@")[-1]:
                print("Error: El email ingresado no tiene un formato válido.")
                return
            fecha_inscripcion = input(
                "Fecha de inscripción (dd/mm/yyyy): ").strip()
            try:
                fecha_inscripcion_dt = datetime.strptime(
                    fecha_inscripcion, "%d/%m/%Y").date()
            except ValueError:
                print("Error: Formato de fecha inválido. Debe ser dd/mm/yyyy.")
                return
            try:
                cuota_social = float(input("Cuota social: "))
                if cuota_social <= 0:
                    print("Error: La cuota social debe ser un número positivo.")
                    return
            except ValueError:
                print("Error: La cuota social debe ser un número.")
                return

            # Solicitar el método de pago
            metodo_pago = input(
                "Método de pago (Efectivo, Debito, Credito, Transferencia): ").capitalize()
            fecha_vencimiento = fecha_inscripcion_dt + timedelta(days=30)
            with self.conectar_db() as conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO socios (dni, nombre, apellido, domicilio, telefono, email, fecha_inscripcion, cuota_social, fecha_vencimiento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (dni, nombre, apellido, domicilio, telefono, email, fecha_inscripcion_dt, cuota_social, fecha_vencimiento))

                # Registrar el pago de la cuota social en la tabla rendicion_cuentas
                fecha_pago = datetime.now().date()  # Fecha del pago (hoy)
                cursor.execute("""
                    INSERT INTO rendicion_cuentas (dni, monto, tipo_pago, metodo_pago, fecha_pago, tipo_persona, fecha_vencimiento)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (dni, cuota_social, "Cuota Social", metodo_pago, fecha_pago, "Socio", fecha_vencimiento))
                conexion.commit()
                print(
                    f"Socia/o {nombre} {apellido} registrado exitosamente y su pago de cuota social registrado en la rendición de cuentas.")
                # Generar el ticket de pago automáticamente
                self.generar_ticket_pago(
                    dni, cuota_social, "Cuota Social", metodo_pago, fecha_pago, fecha_vencimiento, "Socio")
                print("Ticket de pago generado exitosamente.")
        except Exception as e:
            print(f"Error al registrar socio: {e}")

    def modificar_socio(self):
        try:
            dni = input("Ingrese el DNI del socio a modificar: ")

            with self.conectar_db() as conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT * FROM socios WHERE dni = ?", (dni,))
                socio = cursor.fetchone()

                if socio:
                    # Solicitar nuevos datos, o mantener los existentes si no se ingresan
                    nombre = input(f"Nombre ({socio[2]}): ") or socio[2]
                    apellido = input(f"Apellido ({socio[3]}): ") or socio[3]
                    domicilio = input(f"Domicilio ({socio[4]}): ") or socio[4]
                    telefono = input(f"Teléfono ({socio[5]}): ") or socio[5]
                    email = input(f"Email ({socio[6]}): ") or socio[6]
                    cuota_social = float(
                        input(f"Cuota social ({socio[8]}): ") or socio[8])
                    cursor.execute("""
                        UPDATE socios
                        SET nombre = ?, apellido = ?, domicilio = ?, telefono = ?, email = ?, cuota_social = ?
                        WHERE dni = ?
                    """, (nombre, apellido, domicilio, telefono, email, cuota_social, dni))
                    conexion.commit()
                    print(f"Datos de socio {nombre} {apellido} actualizados.")
                else:
                    print("Socio no encontrado.")
        except Exception as e:
            print(f"Error al modificar socio: {e}")

    def eliminar_socio(self):
        try:
            dni = input("Ingrese el DNI del socio a eliminar: ")
            with self.conectar_db() as conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT * FROM socios WHERE dni = ?", (dni,))
                socio = cursor.fetchone()
                if socio:
                    confirmacion = input(f"¿Está seguro de que desea eliminar al socio con DNI {
                                         dni}? (s/n): ").lower()
                    if confirmacion == 's':
                        try:
                            cursor.execute(
                                "DELETE FROM socios WHERE dni = ?", (dni,))
                            conexion.commit()
                            print(f"Socio con DNI {
                                  dni} eliminado exitosamente.")
                        except Exception as e:
                            print(f"Error al eliminar socio: {e}")
                    else:
                        print("Eliminación cancelada.")
                else:
                    print(f"No se encontró un socio con el DNI {dni}.")
        except Exception as e:
            print(f"Error al eliminar socio: {e}")

    def listar_socios(self):
        try:
            with self.conectar_db() as conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT * FROM socios")
                socios = cursor.fetchall()

                if socios:
                    print("Lista de socios:")
                    for socio in socios:
                        print(f"ID: {socio[0]}, DNI: {socio[1]}, Nombre: {socio[2]}, Apellido: {socio[3]}, "
                              f"Domicilio: {socio[4]}, Teléfono: {socio[5]}, Email: {socio[6]}")
                else:
                    print("No hay socios registrados.")
        except Exception as e:
            print(f"Error al listar socios: {e}")

    def gestionar_invitados(self):
        while True:
            print("\n--- Gestionar Invitados ---")
            print("1. Registrar Invitado")
            print("2. Eliminar Invitado")
            print("3. Listar Invitados")
            print("4. Volver")
            opcion = input("Seleccione una opcion: ")

            if opcion == '1':
                self.registrar_invitado()
            elif opcion == '2':
                self.eliminar_invitado()
            elif opcion == '3':
                self.listar_invitados()
            elif opcion == '4':
                break
            else:
                print("Opción inválida, intente nuevamente.")

    def registrar_invitado(self):
        dni_socio = input("DNI del socio que invita: ")

        # Validar que el DNI del socio contenga solo números y tenga una longitud típica
        if not dni_socio.isdigit() or not (7 <= len(dni_socio) <= 8):
            print(
                "Error: El DNI del socio debe contener solo números y tener entre 7 y 8 dígitos.")
            return

        try:
            with self.conectar_db() as conexion:
                cursor = conexion.cursor()

                # Verificar si el socio existe
                cursor.execute(
                    "SELECT dni FROM socios WHERE dni = ?", (dni_socio,))
                socio = cursor.fetchone()
                if not socio:
                    print("Error: Socio no encontrado.")
                    return

                # Verificar que el socio no tenga más de 3 invitados
                cursor.execute(
                    "SELECT COUNT(*) FROM invitados WHERE socio_dni = ?", (dni_socio,))
                num_invitados = cursor.fetchone()[0]
                if num_invitados >= 3:
                    print("Error: El socio ya tiene el máximo de 3 invitados.")
                    return

                # Validar el nombre (permitir tildes y caracteres especiales)
                nombre = input("Nombre: ").strip().capitalize()
                if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", nombre) or len(nombre) < 2:
                    print(
                        "Error: El nombre debe contener solo letras (incluyendo tildes y ñ) y tener al menos 2 caracteres.")
                    return

                # Validar el apellido
                apellido = input("Apellido: ").strip().capitalize()
                if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", apellido) or len(apellido) < 2:
                    print(
                        "Error: El apellido debe contener solo letras (incluyendo tildes y ñ) y tener al menos 2 caracteres.")
                    return

                dni = input("DNI del invitado: ")
                if not dni.isdigit() or not (7 <= len(dni) <= 8):
                    print(
                        "Error: El DNI del invitado debe contener solo números y tener entre 7 y 8 dígitos.")
                    return

                # Verificar si el invitado ya está registrado
                cursor.execute(
                    "SELECT dni FROM invitados WHERE dni = ?", (dni,))
                invitado_existente = cursor.fetchone()
                if invitado_existente:
                    print("Error: El DNI del invitado ya está registrado.")
                    return

                # Insertar el nuevo invitado en la base de datos
                cursor.execute("""
                    INSERT INTO invitados (nombre, apellido, dni, socio_dni)
                    VALUES (?, ?, ?, ?)
                """, (nombre, apellido, dni, dni_socio))
                conexion.commit()
                print("Invitado registrado exitosamente.")

        except Exception as e:
            print(f"Error al registrar invitado: {e}")

    def eliminar_invitado(self):
        dni_invitado = input(
            "Ingrese el DNI del invitado que desea eliminar: ")
        if not dni_invitado.isdigit():
            print("Error: El DNI debe contener solo números.")
            return
        try:
            with self.conectar_db() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    "SELECT dni FROM invitados WHERE dni = ?", (dni_invitado,))
                invitado = cursor.fetchone()

                if not invitado:
                    print("Error: El invitado no está registrado.")
                    return
                cursor.execute(
                    "DELETE FROM invitados WHERE dni = ?", (dni_invitado,))
                conexion.commit()
                print(f"Invitado con DNI {
                      dni_invitado} eliminado exitosamente.")

        except Exception as e:
            print(f"Error al eliminar el invitado: {e}")

    def listar_invitados(self):
        try:
            # Usar el contexto de `with` para la conexión y el cursor
            with self.conectar_db() as conexion:
                cursor = conexion.cursor()

                # Consultar todos los invitados registrados en la base de datos
                cursor.execute(
                    "SELECT dni, nombre, apellido, socio_dni FROM invitados")
                invitados = cursor.fetchall()

                if not invitados:
                    print("No hay invitados registrados.")
                    return

                print("Lista de invitados registrados:")
                for invitado in invitados:
                    dni_invitado, nombre, apellido, dni_socio = invitado
                    print(f"DNI: {dni_invitado} | Nombre: {nombre} | Apellido: {
                          apellido} | Socio que invita (DNI): {dni_socio}")

        except Exception as e:
            print(f"Error al listar los invitados: {e}")

    def gestionar_no_socios(self):
        while True:
            print("\n--- Gestionar No Socios ---")
            print("1. Registrar No Socio")
            print("2. Eliminar No Socio")
            print("3. Listar No Socios")
            print("4. Salir")

            opcion = input("Seleccione una opcion: ")

            if opcion == '1':
                self.registrar_no_socio()
            elif opcion == '2':
                self.eliminar_no_socio()
            elif opcion == '3':
                self.listar_no_socios()
            elif opcion == '4':
                break
            else:
                print("Opcion no valida. Por favor, seleccione una opcion valida.")

    def registrar_no_socio(self):
        try:
            dni = input("DNI del no socio: ")

            # Validación para asegurarse de que el DNI sea numérico y tenga una longitud adecuada
            if not dni.isdigit() or not (7 <= len(dni) <= 8):
                print(
                    "Error: El DNI debe contener solo números y tener entre 7 y 8 dígitos.")
                return

            # Conectar a la base de datos
            with self.conectar_db() as conexion:
                cursor = conexion.cursor()

                # Verificar si el no socio ya está registrado
                cursor.execute(
                    "SELECT dni FROM no_socios WHERE dni = ?", (dni,))
                no_socio_existente = cursor.fetchone()
                if no_socio_existente:
                    print("Error: El DNI ya está registrado como no socio.")
                    return

                # Validar el nombre (permitir tildes y caracteres especiales)
                nombre = input("Nombre: ").strip().capitalize()
                if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", nombre) or len(nombre) < 2:
                    print(
                        "Error: El nombre debe contener solo letras (incluyendo tildes y ñ) y tener al menos 2 caracteres.")
                    return

                # Validar el apellido
                apellido = input("Apellido: ").strip().capitalize()
                if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", apellido) or len(apellido) < 2:
                    print(
                        "Error: El apellido debe contener solo letras (incluyendo tildes y ñ) y tener al menos 2 caracteres.")
                    return

                # Solicitar y validar el teléfono
                telefono = input("Teléfono: ")
                if not telefono.isdigit() or len(telefono) < 7:
                    print(
                        "Error: El teléfono debe contener solo números y tener al menos 7 dígitos.")
                    return

                # Solicitar y validar el email
                email = input("Email: ")
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    print("Error: El formato del email es incorrecto.")
                    return

                # Insertar en la base de datos si todas las validaciones son correctas
                cursor.execute("""
                    INSERT INTO no_socios (dni, nombre, apellido, telefono, email)
                    VALUES (?, ?, ?, ?, ?)
                """, (dni, nombre, apellido, telefono, email))
                conexion.commit()
                print(f"No socio {nombre} {apellido} registrado exitosamente.")
        except Exception as e:
            print(f"Error al registrar no socio: {e}")

    def eliminar_no_socio(self):
        dni_no_socio = input(
            "Ingrese el DNI del no socio que desea eliminar: ")
        if not dni_no_socio.isdigit():
            print("Error: El DNI debe contener solo números.")
            return
        try:
            with self.conectar_db() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    "SELECT dni FROM no_socios WHERE dni = ?", (dni_no_socio,))
                no_socio = cursor.fetchone()
                if not no_socio:
                    print("Error: El no socio no está registrado.")
                    return
                cursor.execute(
                    "DELETE FROM no_socios WHERE dni = ?", (dni_no_socio,))
                conexion.commit()
                print(f"No socio con DNI {
                      dni_no_socio} eliminado exitosamente.")
        except Exception as e:
            print(f"Error al eliminar el no socio: {e}")

    def listar_no_socios(self):
        try:
            with self.conectar_db() as conexion:
                cursor = conexion.cursor()

                cursor.execute("SELECT * FROM no_socios")
                no_socios = cursor.fetchall()

                if no_socios:
                    print("Lista de no socios:")
                    for no_socio in no_socios:
                        print(f"ID: {no_socio[0]}, DNI: {no_socio[1]}, Nombre: {no_socio[2]}, Apellido: {
                              no_socio[3]}, Teléfono: {no_socio[4]}, Email: {no_socio[5]}")
                else:
                    print("No hay no socios registrados.")
        except Exception as e:
            print(f"Error al listar no socios: {e}")

    def pagar_cuota_deportiva(self):
        with self.conectar_db() as conexion:
            cursor = conexion.cursor()
            dni = input("DNI del socio, invitado o no socio: ")

            # Verificar si el usuario es socio, invitado o no socio
            cursor.execute("SELECT dni FROM socios WHERE dni = ?", (dni,))
            socio = cursor.fetchone()

            if socio:
                tipo_persona = "Socio"
                descuento = 0.30
            else:
                cursor.execute(
                    "SELECT socio_dni FROM invitados WHERE dni = ?", (dni,))
                invitado = cursor.fetchone()
                if invitado:
                    tipo_persona = "Invitado"
                    descuento = 0.30
                else:
                    tipo_persona = "No Socio"
                    descuento = 0.00

            # Solicitar el deporte y obtener el monto de la cuota y cupo disponible
            deporte = input(
                "Ingrese el nombre del deporte (Futbol, Tenis, Natacion): ").capitalize()
            cursor.execute(
                "SELECT cuota, cupos FROM deportes WHERE nombre = ?", (deporte,))
            deporte_info = cursor.fetchone()

            if not deporte_info:
                print(f"Deporte {deporte} no encontrado.")
                return

            cuota_deporte, cupos_totales = deporte_info

            # Verificar si el usuario ya está inscrito en el deporte
            cursor.execute(
                "SELECT COUNT(*) FROM inscripciones WHERE dni_socio = ? AND nombre = ?", (dni, deporte))
            inscrito = cursor.fetchone()[0]

            if inscrito > 0:
                print(f"El usuario con DNI {dni} ya está inscrito en {
                      deporte}. No se puede inscribir nuevamente.")
                return

            # Contar el número de inscritos en el deporte para verificar los cupos
            cursor.execute(
                "SELECT COUNT(*) FROM inscripciones WHERE nombre = ?", (deporte,))
            inscritos_actuales = cursor.fetchone()[0]

            if inscritos_actuales >= cupos_totales:
                print(f"No hay cupos disponibles para {deporte}.")
                return

            # Calcular el monto a pagar con descuento si aplica
            monto_a_pagar = cuota_deporte * (1 - descuento)

            # Validar el método de pago
            metodos_validos = ['Efectivo', 'Credito',
                               'Debito', 'Transferencia']
            while True:
                metodo_pago = input(
                    "Ingrese el método de pago (Efectivo, Credito, Debito, Transferencia): ").capitalize()
                if metodo_pago in metodos_validos:
                    print(f"Método de pago '{
                          metodo_pago}' seleccionado correctamente.")
                    break
                else:
                    print("Método de pago no válido. Por favor, ingrese uno de los siguientes métodos: Efectivo, Tarjeta de Crédito, Tarjeta de Débito, Transferencia.")

            # Confirmar si desea realizar el pago
            confirmar_pago = input(f"El monto a pagar para {deporte} es de {
                                   monto_a_pagar:.2f}. ¿Desea proceder con el pago? (S/N): ").strip().upper()
            if confirmar_pago != "S":
                print("Pago cancelado.")
                return

            # Establecer fecha de pago y fecha de vencimiento
            fecha_pago = datetime.now().date()
            fecha_vencimiento = fecha_pago + timedelta(days=30)

            try:
                # Registrar el pago en la tabla de rendición de cuentas
                cursor.execute("""
                    INSERT INTO rendicion_cuentas (dni, monto, tipo_pago, metodo_pago, fecha_pago, fecha_vencimiento, tipo_persona)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (dni, monto_a_pagar, f"Cuota {deporte}", metodo_pago, fecha_pago, fecha_vencimiento, tipo_persona))

                # Registrar en inscripciones
                cursor.execute("""
                    INSERT INTO inscripciones (dni_socio, nombre, cuota)
                    VALUES (?, ?, ?)
                """, (dni, deporte, monto_a_pagar))

                # Confirmar los cambios en la base de datos
                conexion.commit()
                print(f"El pago de la cuota de {deporte} por {
                      tipo_persona} ha sido registrado exitosamente. Monto: {monto_a_pagar:.2f}")
                print(f"Fecha de vencimiento de la cuota: {fecha_vencimiento}")

                # Generar el ticket de pago automáticamente
                self.generar_ticket_pago(dni, monto_a_pagar, f"Cuota {
                                         deporte}", metodo_pago, fecha_pago, fecha_vencimiento, tipo_persona)
                print("Ticket de pago generado exitosamente.")
            except Exception as e:
                print(f"Error al registrar el pago de la cuota deportiva: {e}")
                conexion.rollback()

    def rendir_cuentas(self):
        while True:
            print("\n--- Menú de Rendición de Cuentas ---")
            print("1: Buscar rendimiento por un mes específico")
            print("2: Ver rendimiento del último mes")
            print("3: Rendimiento general de todos los pagos")
            print("4: Generar reporte completo y buscar por mes")
            print("5: Salir")
            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                mes = input("Ingrese el mes en formato MM-AAAA: ")
                self.obtener_rendimiento_mes(mes)
            elif opcion == '2':
                # Llamar sin mes para obtener el rendimiento del último mes
                self.obtener_rendimiento_mes()
            elif opcion == '3':
                self.rendimiento_general()
            elif opcion == '4':
                mes = input(
                    "Ingrese el mes en formato MM-AAAA para el reporte: ")
                self.generar_reporte_mes_txt(mes)
            elif opcion == '5':
                print("Saliendo del menú.")
                break
            else:
                print("Opción no válida, intenta nuevamente.")

    def obtener_rendimiento_mes(self, mes=None):
        with self.conectar_db() as conexion:
            cursor = conexion.cursor()
            try:
                if mes:
                    primer_dia_mes = datetime.strptime(
                        mes, "%m-%Y").replace(day=1)
                else:
                    fecha_actual = datetime.now()
                    primer_dia_mes = fecha_actual.replace(day=1)

                ultimo_dia_mes = (primer_dia_mes + timedelta(days=32)
                                  ).replace(day=1) - timedelta(days=1)

                # Reiniciar el total para el mes
                total_mes = 0

                # Mostrar pagos de cuota social
                cursor.execute("""
                    SELECT dni, monto, tipo_pago, metodo_pago, fecha_pago, tipo_persona
                    FROM rendicion_cuentas
                    WHERE tipo_pago = 'Cuota Social' AND fecha_pago BETWEEN ? AND ?
                    ORDER BY fecha_pago DESC
                """, (primer_dia_mes.strftime("%Y-%m-%d"), ultimo_dia_mes.strftime("%Y-%m-%d")))
                pagos_sociales = cursor.fetchall()

                if pagos_sociales:
                    print("\n--- Rendición de Cuentas Mensual - Cuota Social ---")
                    for pago in pagos_sociales:
                        self.mostrar_detalle_pago(pago)

                # Mostrar pagos de cuota deportiva
                cursor.execute("""
                    SELECT dni, monto, tipo_pago, metodo_pago, fecha_pago, tipo_persona
                    FROM rendicion_cuentas
                    WHERE tipo_pago LIKE 'Cuota %' AND tipo_pago != 'Cuota Social' AND fecha_pago BETWEEN ? AND ?
                    ORDER BY fecha_pago DESC
                """, (primer_dia_mes.strftime("%Y-%m-%d"), ultimo_dia_mes.strftime("%Y-%m-%d")))
                pagos_deportivos = cursor.fetchall()

                if pagos_deportivos:
                    print("\n--- Rendición de Cuentas Mensual - Cuota Deportiva ---")
                    for pago in pagos_deportivos:
                        self.mostrar_detalle_pago(pago)

                # Resumen de pagos del mes (sin duplicar el total)
                cursor.execute("""
                    SELECT tipo_pago, SUM(monto)
                    FROM rendicion_cuentas
                    WHERE fecha_pago BETWEEN ? AND ?
                    GROUP BY tipo_pago
                """, (primer_dia_mes.strftime("%Y-%m-%d"), ultimo_dia_mes.strftime("%Y-%m-%d")))
                resumen = cursor.fetchall()

                print("\n--- Resumen de Pagos del Mes ---")
                for tipo_pago, total in resumen:
                    print(f"{tipo_pago}: {total:.2f}")
                    total_mes += total

                # Mostrar el total del mes
                print(f"\nTotal de todos los pagos en el mes: ${
                      total_mes:.2f}")
            except Exception as e:
                print(f"Error al obtener la rendición de cuentas: {e}")

    def rendimiento_general(self):
        with self.conectar_db() as conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("""
                    SELECT tipo_pago, SUM(monto)
                    FROM rendicion_cuentas
                    GROUP BY tipo_pago
                """)
                resumen = cursor.fetchall()
                total_general = 0  # Variable para almacenar el total general

                print("\n--- Rendimiento General ---")
                for tipo_pago, total in resumen:
                    print(f"{tipo_pago}: {total:.2f}")
                    total_general += total  # Acumular el monto en total general

                # Mostrar el total general
                print(f"\nTotal general de todos los pagos: ${
                    total_general:.2f}")
            except Exception as e:
                print(f"Error al obtener el rendimiento general: {e}")

    def mostrar_detalle_pago(self, pago):
        dni, monto, tipo_pago, metodo_pago, fecha_pago, tipo_persona = pago
        fecha_pago_formateada = datetime.strptime(
            fecha_pago, "%Y-%m-%d").strftime("%d/%m/%Y")
        print(f"\nDNI: {dni}")
        print(f"Tipo de Persona: {tipo_persona}")
        print(f"Tipo de Pago: {tipo_pago}")
        print(f"Método de Pago: {metodo_pago}")
        print(f"Monto: ${monto:.2f}")
        print(f"Fecha de Pago: {fecha_pago_formateada}")
        print("-" * 30)

        # Generar el ticket por cada pago
        fecha_vencimiento = datetime.strptime(
            fecha_pago, '%Y-%m-%d') + timedelta(days=30)
        self.generar_ticket_pago(dni, monto, tipo_pago, metodo_pago, fecha_pago_formateada,
                                 fecha_vencimiento.strftime("%d/%m/%Y"), tipo_persona)

    def generar_reporte_mes_txt(self, mes):
        with self.conectar_db() as conexion:
            cursor = conexion.cursor()
            try:
                primer_dia_mes = datetime.strptime(mes, "%m-%Y").replace(day=1)
                ultimo_dia_mes = (primer_dia_mes + timedelta(days=32)
                                  ).replace(day=1) - timedelta(days=1)

                # Nombre del archivo de reporte
                nombre_archivo = f"reporte_{mes}.txt"

                with open(nombre_archivo, 'w') as archivo:
                    archivo.write(
                        f"--- Reporte de Rendición de Cuentas para {mes} ---\n\n")

                    total_mes = 0  # Variable para almacenar el total del mes

                    # Obtener pagos de cuota social
                    cursor.execute("""
                        SELECT dni, monto, tipo_pago, metodo_pago, fecha_pago, tipo_persona
                        FROM rendicion_cuentas
                        WHERE tipo_pago = 'Cuota Social' AND fecha_pago BETWEEN ? AND ?
                        ORDER BY fecha_pago DESC
                    """, (primer_dia_mes.strftime("%Y-%m-%d"), ultimo_dia_mes.strftime("%Y-%m-%d")))
                    pagos_sociales = cursor.fetchall()

                    archivo.write("\n--- Detalles de Cuota Social ---\n")
                    for pago in pagos_sociales:
                        archivo.write(self.formatear_pago(pago))
                        total_mes += pago[1]

                    # Obtener pagos de cuota deportiva
                    cursor.execute("""
                        SELECT dni, monto, tipo_pago, metodo_pago, fecha_pago, tipo_persona
                        FROM rendicion_cuentas
                        WHERE tipo_pago LIKE 'Cuota %' AND tipo_pago != 'Cuota Social' AND fecha_pago BETWEEN ? AND ?
                        ORDER BY fecha_pago DESC
                    """, (primer_dia_mes.strftime("%Y-%m-%d"), ultimo_dia_mes.strftime("%Y-%m-%d")))
                    pagos_deportivos = cursor.fetchall()

                    archivo.write("\n--- Detalles de Cuota Deportiva ---\n")
                    for pago in pagos_deportivos:
                        archivo.write(self.formatear_pago(pago))
                        total_mes += pago[1]

                    # Resumen de pagos
                    archivo.write("\n--- Resumen de Pagos del Mes ---\n")
                    cursor.execute("""
                        SELECT tipo_pago, SUM(monto)
                        FROM rendicion_cuentas
                        WHERE fecha_pago BETWEEN ? AND ?
                        GROUP BY tipo_pago
                    """, (primer_dia_mes.strftime("%Y-%m-%d"), ultimo_dia_mes.strftime("%Y-%m-%d")))
                    resumen = cursor.fetchall()

                    for tipo_pago, total in resumen:
                        archivo.write(f"{tipo_pago}: {total:.2f}\n")

                    archivo.write(f"\nTotal de todos los pagos en el mes: {
                                  total_mes:.2f}\n")

                print(f"Reporte generado correctamente en {nombre_archivo}")

            except Exception as e:
                print(f"Error al generar el reporte: {e}")

    def formatear_pago(self, pago):
        dni, monto, tipo_pago, metodo_pago, fecha_pago, tipo_persona = pago
        fecha_pago_formateada = datetime.strptime(
            fecha_pago, "%Y-%m-%d").strftime("%d/%m/%Y")
        return (f"DNI: {dni}\n"
                f"Tipo de Persona: {tipo_persona}\n"
                f"Tipo de Pago: {tipo_pago}\n"
                f"Método de Pago: {metodo_pago}\n"
                f"Monto: {monto:.2f}\n"
                f"Fecha de Pago: {fecha_pago_formateada}\n"
                f"{'-' * 30}\n")

    def generar_ticket_pago(self, dni, monto, tipo_pago, metodo_pago, fecha_pago, fecha_vencimiento, tipo_persona):
        try:
            ticket = f"""
            ===========================================
                    TICKET DE PAGO
            ===========================================
            DNI: {dni}
            Tipo de Persona: {tipo_persona}
            Tipo de Pago: {tipo_pago}
            Método de Pago: {metodo_pago}
            Monto Pagado: ${monto:.2f}
            Fecha de Pago: {fecha_pago}
            Fecha de Vencimiento: {fecha_vencimiento}
            ===========================================
            ¡Gracias por realizar el pago!
            ===========================================
            """
            print(ticket)

            # Crear nombre del archivo de ticket
            nombre_archivo = f"ticket_pago_{dni}_{tipo_pago.replace(' ', '_')}_{
                metodo_pago.replace(' ', '_')}.txt"
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write(ticket)
            # Guardar el ticket en un archivo de texto
            print(f"El ticket ha sido guardado en {nombre_archivo}.")
        except Exception as e:
            print(f"Error al generar el ticket: {e}")
