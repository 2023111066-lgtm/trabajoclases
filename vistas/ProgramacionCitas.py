"""Vista del módulo Citas: programar, listar, reprogramar y cancelar (Tkinter)."""
import tkinter as tk
from tkinter import messagebox, ttk

from clases.Cita import Cita

CAMPOS = ("dni", "fecha", "hora", "motivo")


class ProgramacionCitas(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.id_actual = None  # None = cita nueva; con valor = cita seleccionada
        self.vars = {c: tk.StringVar() for c in CAMPOS}
        self._crear_widgets()
        self.cargar_lista()

    def _crear_widgets(self):
        # ----- Formulario -----
        marco = ttk.LabelFrame(self, text="Datos de la cita", padding=10)
        marco.grid(row=0, column=0, sticky="n", padx=(0, 10))
        etiquetas = [
            ("DNI del paciente *", "dni"),
            ("Fecha (AAAA-MM-DD) *", "fecha"),
            ("Hora (HH:MM) *", "hora"),
            ("Motivo *", "motivo"),
        ]
        self.entradas = {}
        for fila, (texto, campo) in enumerate(etiquetas):
            ttk.Label(marco, text=texto).grid(row=fila, column=0, sticky="w", pady=3)
            w = ttk.Entry(marco, textvariable=self.vars[campo], width=30)
            w.grid(row=fila, column=1, pady=3, padx=(8, 0))
            self.entradas[campo] = w
        botones = ttk.Frame(marco)
        botones.grid(row=len(etiquetas), column=0, columnspan=2, pady=(12, 0))
        ttk.Button(botones, text="Programar", command=self.programar).grid(row=0, column=0, padx=4, pady=2)
        ttk.Button(botones, text="Reprogramar", command=self.reprogramar).grid(row=0, column=1, padx=4, pady=2)
        ttk.Button(botones, text="Cancelar cita", command=self.cancelar).grid(row=1, column=0, padx=4, pady=2)
        ttk.Button(botones, text="Nuevo", command=self.limpiar).grid(row=1, column=1, padx=4, pady=2)
        self.lbl_modo = ttk.Label(marco, text="Modo: programar cita nueva", foreground="#0b7a6e")
        self.lbl_modo.grid(row=len(etiquetas) + 1, column=0, columnspan=2, pady=(8, 0))

        # ----- Lista -----
        derecha = ttk.Frame(self)
        derecha.grid(row=0, column=1, sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        columnas = ("id", "dni", "paciente", "fecha", "hora", "motivo", "estado")
        self.tabla = ttk.Treeview(derecha, columns=columnas, show="headings", height=14, selectmode="browse")
        anchos = (40, 90, 170, 90, 60, 150, 90)
        for col, ancho in zip(columnas, anchos):
            self.tabla.heading(col, text=col.capitalize())
            self.tabla.column(col, width=ancho, anchor="w")
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar)

    # ----- Acciones -----
    def cargar_lista(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for c in Cita.listar():
            self.tabla.insert("", "end", values=(c["id_cita"], c["dni"], c["paciente"], c["fecha"],
                                                 c["hora"], c["motivo"], c["estado"]))

    def _datos(self):
        return {c: self.vars[c].get().strip() for c in CAMPOS}

    def limpiar(self):
        self.id_actual = None
        for v in self.vars.values():
            v.set("")
        self.entradas["dni"].config(state="normal")
        self.lbl_modo.config(text="Modo: programar cita nueva")
        self.tabla.selection_remove(self.tabla.selection())

    def seleccionar(self, _evento=None):
        """Al elegir una fila se cargan sus datos en el formulario."""
        sel = self.tabla.selection()
        if not sel:
            return
        id_cita = self.tabla.item(sel[0], "values")[0]
        c = Cita.obtener(id_cita)
        if c is None:
            return
        self.id_actual = c["id_cita"]
        self.entradas["dni"].config(state="normal")
        for campo in CAMPOS:
            self.vars[campo].set(c[campo])
        self.entradas["dni"].config(state="readonly")
        self.lbl_modo.config(text=f"Modo: cita #{c['id_cita']} seleccionada ({c['estado']})")

    def programar(self):
        if self.id_actual is not None:
            messagebox.showwarning("Cita seleccionada",
                                   "Hay una cita seleccionada. Presione \"Nuevo\" para programar otra.")
            return
        errores = Cita(**self._datos()).programar()
        if errores:
            messagebox.showerror("Datos no válidos", "\n".join(errores))
            return
        messagebox.showinfo("Listo", "Cita programada correctamente.")
        self.limpiar()
        self.cargar_lista()

    def reprogramar(self):
        if self.id_actual is None:
            messagebox.showwarning("Seleccione una cita", "Seleccione una cita de la tabla.")
            return
        datos = self._datos()
        errores = Cita(id_cita=self.id_actual, **datos).reprogramar()
        if errores:
            messagebox.showerror("Datos no válidos", "\n".join(errores))
            return
        messagebox.showinfo("Listo", "Cita reprogramada correctamente.")
        self.limpiar()
        self.cargar_lista()

    def cancelar(self):
        if self.id_actual is None:
            messagebox.showwarning("Seleccione una cita", "Seleccione una cita de la tabla.")
            return
        actual = Cita.obtener(self.id_actual)
        if actual is not None and actual["estado"] == "Cancelada":
            messagebox.showinfo("Aviso", "Esa cita ya está cancelada.")
            return
        if not messagebox.askyesno("Confirmar", "¿Desea cancelar la cita seleccionada?"):
            return
        Cita.cancelar(self.id_actual)
        messagebox.showinfo("Listo", "Cita cancelada.")
        self.limpiar()
        self.cargar_lista()
