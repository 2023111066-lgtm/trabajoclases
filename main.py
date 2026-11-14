"""Punto de entrada del SIHC-Net12. Ejecutar con:  python main.py"""
import tkinter as tk
from tkinter import ttk

from clases import BaseDatos
from vistas.FormularioPaciente import FormularioPaciente


def main():
    BaseDatos.crear_tablas()
    ventana = tk.Tk()
    ventana.title("SIHC-Net12 - Sistema de Historia Clínica Electrónica")
    ventana.geometry("1000x480")
    pestanas = ttk.Notebook(ventana)
    pestanas.pack(fill="both", expand=True)
    pestanas.add(FormularioPaciente(pestanas), text="Pacientes")
    ventana.mainloop()


if __name__ == "__main__":
    main()