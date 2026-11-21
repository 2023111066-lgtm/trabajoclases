"""Clase Cita: reglas de negocio y acceso a SQLite del módulo Citas (RF04)."""
import re
from datetime import datetime

from clases import BaseDatos


class Cita:
    def __init__(self, dni="", fecha="", hora="", motivo="", estado="Programada", id_cita=None):
        self.id_cita = id_cita
        self.dni = dni
        self.fecha = fecha
        self.hora = hora
        self.motivo = motivo
        self.estado = estado

    # ----- Validaciones -----
    def validar(self):
        """Devuelve una lista de mensajes de error (vacía si todo está bien)."""
        if not (self.dni and self.fecha and self.hora and self.motivo):
            return ["Todos los campos son obligatorios."]

        con = BaseDatos.conectar()
        existe = con.execute("SELECT 1 FROM paciente WHERE dni = ?", (self.dni,)).fetchone()
        con.close()
        if not existe:
            return ["El DNI no corresponde a un paciente registrado."]

        momento = self._convertir_fecha_hora()
        if momento is None:
            return ["Fecha u hora inválida. Use los formatos AAAA-MM-DD y HH:MM."]
        if momento < datetime.now():
            return ["No se aceptan fechas ni horas pasadas."]

        if self._hay_cita_en_ese_horario():
            return ["Ya hay una cita programada en esa fecha y hora."]
        return []

    def _convertir_fecha_hora(self):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", self.fecha):
            return None
        if not re.fullmatch(r"\d{2}:\d{2}", self.hora):
            return None
        try:
            return datetime.strptime(self.fecha + " " + self.hora, "%Y-%m-%d %H:%M")
        except ValueError:
            return None

    def _hay_cita_en_ese_horario(self):
        con = BaseDatos.conectar()
        fila = con.execute(
            "SELECT 1 FROM cita WHERE fecha = ? AND hora = ? AND estado = 'Programada' "
            "AND id_cita IS NOT ?",
            (self.fecha, self.hora, self.id_cita),
        ).fetchone()
        con.close()
        return fila is not None

    # ----- Acciones -----
    def programar(self):
        errores = self.validar()
        if errores:
            return errores
        con = BaseDatos.conectar()
        con.execute(
            "INSERT INTO cita (dni, fecha, hora, motivo, estado) VALUES (?, ?, ?, ?, 'Programada')",
            (self.dni, self.fecha, self.hora, self.motivo),
        )
        con.commit()
        con.close()
        return []

    def reprogramar(self):
        actual = Cita.obtener(self.id_cita)
        if actual is None:
            return ["La cita no existe."]
        if actual["estado"] == "Cancelada":
            return ["No se puede reprogramar una cita cancelada."]
        errores = self.validar()
        if errores:
            return errores
        con = BaseDatos.conectar()
        con.execute(
            "UPDATE cita SET fecha = ?, hora = ?, motivo = ? WHERE id_cita = ?",
            (self.fecha, self.hora, self.motivo, self.id_cita),
        )
        con.commit()
        con.close()
        return []

    @staticmethod
    def cancelar(id_cita):
        con = BaseDatos.conectar()
        con.execute("UPDATE cita SET estado = 'Cancelada' WHERE id_cita = ?", (id_cita,))
        con.commit()
        con.close()

    @staticmethod
    def obtener(id_cita):
        con = BaseDatos.conectar()
        fila = con.execute("SELECT * FROM cita WHERE id_cita = ?", (id_cita,)).fetchone()
        con.close()
        return fila

    @staticmethod
    def listar():
        con = BaseDatos.conectar()
        filas = con.execute(
            "SELECT c.id_cita, c.dni, p.apellidos || ' ' || p.nombres AS paciente, "
            "c.fecha, c.hora, c.motivo, c.estado "
            "FROM cita c JOIN paciente p ON p.dni = c.dni "
            "ORDER BY c.fecha, c.hora"
        ).fetchall()
        con.close()
        return filas
