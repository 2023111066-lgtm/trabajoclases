"""Clase Paciente (RF02: registro y actualización de pacientes)."""
import re
import sqlite3
from datetime import date, datetime

from clases import BaseDatos


class Paciente:
    def __init__(self, dni, nombres, apellidos, fecha_nacimiento, sexo, telefono="", id_paciente=None):
        self.id_paciente = id_paciente
        self.dni = dni
        self.nombres = nombres
        self.apellidos = apellidos
        self.fecha_nacimiento = fecha_nacimiento
        self.sexo = sexo
        self.telefono = telefono

    def validar(self):
        """Devuelve una lista con los errores encontrados (vacía si todo está bien)."""
        errores = []
        if not re.fullmatch(r"\d{8}", self.dni):
            errores.append("El DNI debe tener exactamente 8 dígitos.")
        if not self.nombres:
            errores.append("Los nombres son obligatorios.")
        if not self.apellidos:
            errores.append("Los apellidos son obligatorios.")
        try:
            nacimiento = datetime.strptime(self.fecha_nacimiento, "%Y-%m-%d").date()
            if nacimiento > date.today():
                errores.append("La fecha de nacimiento no puede ser futura.")
        except ValueError:
            errores.append("La fecha de nacimiento no es válida (use AAAA-MM-DD).")
        if self.sexo not in ("M", "F"):
            errores.append("Seleccione el sexo (M o F).")
        if self.telefono and not re.fullmatch(r"\d{9}", self.telefono):
            errores.append("El teléfono debe tener 9 dígitos.")
        return errores

    def registrar(self):
        """Guarda un paciente nuevo. Devuelve la lista de errores (vacía si se guardó)."""
        errores = self.validar()
        if errores:
            return errores
        con = BaseDatos.conectar()
        try:
            cursor = con.execute(
                "INSERT INTO paciente (dni, nombres, apellidos, fecha_nacimiento, sexo, telefono) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (self.dni, self.nombres, self.apellidos, self.fecha_nacimiento, self.sexo, self.telefono),
            )
            con.commit()
            self.id_paciente = cursor.lastrowid
        except sqlite3.IntegrityError:
            return ["Ya existe un paciente con ese DNI."]
        finally:
            con.close()
        return []

    def actualizar_datos(self):
        """Actualiza un paciente existente. Devuelve la lista de errores (vacía si se guardó)."""
        errores = self.validar()
        if errores:
            return errores
        con = BaseDatos.conectar()
        try:
            con.execute(
                "UPDATE paciente SET dni=?, nombres=?, apellidos=?, fecha_nacimiento=?, sexo=?, telefono=? "
                "WHERE id_paciente=?",
                (self.dni, self.nombres, self.apellidos, self.fecha_nacimiento, self.sexo,
                 self.telefono, self.id_paciente),
            )
            con.commit()
        except sqlite3.IntegrityError:
            return ["Ya existe otro paciente con ese DNI."]
        finally:
            con.close()
        return []

    @staticmethod
    def _desde_fila(f):
        return Paciente(f["dni"], f["nombres"], f["apellidos"], f["fecha_nacimiento"],
                        f["sexo"], f["telefono"] or "", f["id_paciente"])

    @staticmethod
    def listar(filtro=""):
        """Lista pacientes; si hay filtro busca por DNI, nombres o apellidos."""
        con = BaseDatos.conectar()
        patron = f"%{filtro.strip()}%"
        filas = con.execute(
            "SELECT * FROM paciente WHERE dni LIKE ? OR nombres LIKE ? OR apellidos LIKE ? "
            "ORDER BY apellidos, nombres",
            (patron, patron, patron),
        ).fetchall()
        con.close()
        return [Paciente._desde_fila(f) for f in filas]

    @staticmethod
    def obtener(id_paciente):
        """Consulta un paciente por su id (None si no existe)."""
        con = BaseDatos.conectar()
        fila = con.execute("SELECT * FROM paciente WHERE id_paciente=?", (id_paciente,)).fetchone()
        con.close()
        return Paciente._desde_fila(fila) if fila else None
