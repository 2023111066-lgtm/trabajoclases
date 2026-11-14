"""Conexión a SQLite y creación de tablas. El archivo sihc.db se crea solo."""
import os
import sqlite3

RUTA_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sihc.db")


def conectar():
    con = sqlite3.connect(RUTA_DB)
    con.row_factory = sqlite3.Row
    return con


def crear_tablas():
    con = conectar()
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS paciente (
            id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT NOT NULL UNIQUE,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL,
            sexo TEXT NOT NULL,
            telefono TEXT
        )
        """
    )
    con.commit()
    con.close()