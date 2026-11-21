"""Vista del módulo Pacientes: formulario + lista + búsqueda (Tkinter)."""
import tkinter as tk
from tkinter import messagebox, ttk

from clases.Paciente import Paciente

CAMPOS = ("dni", "nombres", "apellidos", "fecha_nacimiento", "sexo", "telefono")


class FormularioPaciente(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.id_actual = None  # None = paciente nuevo; con valor = actualizando
        self.vars = {c: tk.StringVar() for c in CAMPOS}
        self.var_busqueda = tk.StringVar()
        self._crear_widgets()
        self.cargar_lista()

    def _crear_widgets(self):
        # ----- Formulario -----
        marco = ttk.LabelFrame(self, text="Datos del paciente", padding=10)
        marco.grid(row=0, column=0, sticky="n", padx=(0, 10))
        etiquetas = [
            ("DNI (8 dígitos) *", "dni"),
            ("Nombres *", "nombres"),
            ("Apellidos *", "apellidos"),
            ("Nacimiento (AAAA-MM-DD) *", "fecha_nacimiento"),
            ("Sexo *", "sexo"),
            ("Teléfono (9 dígitos)", "telefono"),
        ]
        for fila, (texto, campo) in enumerate(etiquetas):
            ttk.Label(marco, text=texto).grid(row=fila, column=0, sticky="w", pady=3)
            if campo == "sexo":
                w = ttk.Combobox(marco, textvariable=self.vars[campo], values=("M", "F"),
                                 state="readonly", width=27)
            else:
                w = ttk.Entry(marco, textvariable=self.vars[campo], width=30)
            w.grid(row=fila, column=1, pady=3, padx=(8, 0))
        botones = ttk.Frame(marco)
        botones.grid(row=len(etiquetas), column=0, columnspan=2, pady=(12, 0))
        ttk.Button(botones, text="Guardar", command=self.guardar).pack(side="left", padx=4)
        ttk.Button(botones, text="Nuevo", command=self.limpiar).pack(side="left", padx=4)
        self.lbl_modo = ttk.Label(marco, text="Modo: registrar paciente nuevo", foreground="#0b7a6e")
        self.lbl_modo.grid(row=len(etiquetas) + 1, column=0, columnspan=2, pady=(8, 0))

        # ----- Lista y búsqueda -----
        derecha = ttk.Frame(self)
        derecha.grid(row=0, column=1, sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        barra = ttk.Frame(derecha)
        barra.pack(fill="x", pady=(0, 6))
        ttk.Label(barra, text="Buscar (DNI, nombres o apellidos):").pack(side="left")
        ttk.Entry(barra, textvariable=self.var_busqueda, width=22).pack(side="left", padx=6)
        ttk.Button(barra, text="Buscar", command=lambda: self.cargar_lista(self.var_busqueda.get())).pack(side="left")
        ttk.Button(barra, text="Ver todos", command=self._ver_todos).pack(side="left", padx=4)

        columnas = ("id", "dni", "apellidos", "nombres", "nacimiento", "sexo", "telefono")
        self.tabla = ttk.Treeview(derecha, columns=columnas, show="headings", height=14, selectmode="browse")
        anchos = (40, 90, 140, 140, 100, 50, 90)
        for col, ancho in zip(columnas, anchos):
            self.tabla.heading(col, text=col.capitalize())
            self.tabla.column(col, width=ancho, anchor="w")
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar)

    # ----- Acciones -----
    def cargar_lista(self, filtro=""):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for p in Paciente.listar(filtro):
            self.tabla.insert("", "end", values=(p.id_paciente, p.dni, p.apellidos, p.nombres,
                                                 p.fecha_nacimiento, p.sexo, p.telefono))

    def _ver_todos(self):
        self.var_busqueda.set("")
        self.cargar_lista()

    def limpiar(self):
        self.id_actual = None
        for v in self.vars.values():
            v.set("")
        self.lbl_modo.config(text="Modo: registrar paciente nuevo")
        self.tabla.selection_remove(self.tabla.selection())

    def seleccionar(self, _evento=None):
        """Consultar: al elegir una fila se cargan sus datos en el formulario."""
        sel = self.tabla.selection()
        if not sel:
            return
        id_paciente = self.tabla.item(sel[0], "values")[0]
        p = Paciente.obtener(id_paciente)
        if p is None:
            return
        self.id_actual = p.id_paciente
        for campo in CAMPOS:
            self.vars[campo].set(getattr(p, campo) or "")
        self.lbl_modo.config(text=f"Modo: actualizando paciente #{p.id_paciente}")

    def guardar(self):
        datos = {c: self.vars[c].get().strip() for c in CAMPOS}
        paciente = Paciente(**datos, id_paciente=self.id_actual)
        if self.id_actual is None:
            errores = paciente.registrar()
            mensaje = "Paciente registrado correctamente."
        else:
            errores = paciente.actualizar_datos()
            mensaje = "Datos del paciente actualizados correctamente."
        if errores:
            messagebox.showerror("Datos no válidos", "\n".join(errores))
            return
        messagebox.showinfo("Listo", mensaje)
        self.limpiar()
        self.cargar_lista()
