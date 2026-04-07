import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from app.modelos.usuarios import crear_usuario, obtener_usuarios, eliminar_usuario
from app.modelos.campanas import crear_campana, obtener_campanas, añadir_miembro
from app.modelos.personajes import (crear_personaje, obtener_personajes_de_campana,
                                     obtener_personaje_completo, actualizar_estadisticas)

# ════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ════════════════════════════════════════════════════════
class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("VTT Manager")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e1e2e")

        # Estilo general
        self.estilo = ttk.Style()
        self.estilo.theme_use("clam")
        self._configurar_estilos()

        # Notebook = contenedor de pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Crear cada pestaña
        self._crear_pestaña_usuarios()
        self._crear_pestaña_campanas()
        self._crear_pestaña_personajes()

    def _configurar_estilos(self):
        bg       = "#1e1e2e"
        bg2      = "#2a2a3e"
        fg       = "#cdd6f4"
        accent   = "#89b4fa"
        success  = "#a6e3a1"
        danger   = "#f38ba8"

        self.estilo.configure("TNotebook",
            background=bg, borderwidth=0)
        self.estilo.configure("TNotebook.Tab",
            background=bg2, foreground=fg,
            padding=[12, 6], font=("Segoe UI", 10))
        self.estilo.map("TNotebook.Tab",
            background=[("selected", accent)],
            foreground=[("selected", bg)])
        self.estilo.configure("TFrame",
            background=bg)
        self.estilo.configure("TLabel",
            background=bg, foreground=fg,
            font=("Segoe UI", 10))
        self.estilo.configure("TButton",
            background=accent, foreground=bg,
            font=("Segoe UI", 10, "bold"), padding=[10, 5])
        self.estilo.map("TButton",
            background=[("active", success)])
        self.estilo.configure("Danger.TButton",
            background=danger, foreground=bg,
            font=("Segoe UI", 10, "bold"), padding=[10, 5])
        self.estilo.configure("Treeview",
            background=bg2, foreground=fg,
            fieldbackground=bg2, rowheight=28,
            font=("Segoe UI", 10))
        self.estilo.configure("Treeview.Heading",
            background=bg, foreground=accent,
            font=("Segoe UI", 10, "bold"))
        self.estilo.configure("TEntry",
            fieldbackground=bg2, foreground=fg,
            insertcolor=fg, font=("Segoe UI", 10))
        self.estilo.configure("TLabelframe",
            background=bg, foreground=accent,
            font=("Segoe UI", 10, "bold"))
        self.estilo.configure("TLabelframe.Label",
            background=bg, foreground=accent,
            font=("Segoe UI", 10, "bold"))

        self.colors = {
            "bg": bg, "bg2": bg2, "fg": fg,
            "accent": accent, "success": success, "danger": danger
        }

# ════════════════════════════════════════════════════════
#  PESTAÑA: USUARIOS
# ════════════════════════════════════════════════════════
    def _crear_pestaña_usuarios(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👤 Usuarios")

        # ── Formulario de creación ──
        form = ttk.LabelFrame(frame, text="Nuevo usuario")
        form.pack(fill="x", padx=15, pady=10)

        campos = [("Usuario:", 0), ("Email:", 1), ("Contraseña:", 2)]
        self.entry_usu = {}
        for label, col in campos:
            ttk.Label(form, text=label).grid(
                row=0, column=col*2, padx=(15,5), pady=10, sticky="e")
            key = label.replace(":", "").lower().strip()
            entry = ttk.Entry(form, width=20,
                show="*" if "seña" in label else "")
            entry.grid(row=0, column=col*2+1, padx=(0,15), pady=10)
            self.entry_usu[key] = entry

        ttk.Button(form, text="Crear usuario",
            command=self._crear_usuario).grid(
            row=0, column=6, padx=15, pady=10)

        # ── Tabla de usuarios ──
        cols = ("ID", "Usuario", "Email", "Registro")
        self.tabla_usu = ttk.Treeview(frame, columns=cols,
            show="headings", height=12)
        for col in cols:
            self.tabla_usu.heading(col, text=col)
            self.tabla_usu.column("ID", width=260)
            self.tabla_usu.column("Usuario", width=150)
            self.tabla_usu.column("Email", width=200)
            self.tabla_usu.column("Registro", width=180)
        self.tabla_usu.pack(fill="both", expand=True, padx=15, pady=(0,5))

        # ── Botones de acción ──
        bar = ttk.Frame(frame)
        bar.pack(fill="x", padx=15, pady=(0,10))
        ttk.Button(bar, text="🔄 Actualizar",
            command=self._cargar_usuarios).pack(side="left", padx=5)
        ttk.Button(bar, text="🗑 Eliminar seleccionado",
            style="Danger.TButton",
            command=self._eliminar_usuario).pack(side="left", padx=5)

        self._cargar_usuarios()

    def _crear_usuario(self):
        nombre = self.entry_usu["usuario"].get().strip()
        email  = self.entry_usu["email"].get().strip()
        pw     = self.entry_usu["contraseña"].get().strip()
        if not nombre or not email or not pw:
            messagebox.showwarning("Campos vacíos",
                "Rellena todos los campos.")
            return
        try:
            crear_usuario(nombre, email, pw)
            messagebox.showinfo("Éxito", f"Usuario '{nombre}' creado.")
            for e in self.entry_usu.values():
                e.delete(0, tk.END)
            self._cargar_usuarios()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _cargar_usuarios(self):
        for row in self.tabla_usu.get_children():
            self.tabla_usu.delete(row)
        for u in (obtener_usuarios() or []):
            self.tabla_usu.insert("", "end", values=(
                u["id"], u["nombre_usuario"],
                u["email"], u["fecha_registro"]))

    def _eliminar_usuario(self):
        sel = self.tabla_usu.selection()
        if not sel:
            messagebox.showwarning("Sin selección",
                "Selecciona un usuario.")
            return
        uid  = self.tabla_usu.item(sel[0])["values"][0]
        nombre = self.tabla_usu.item(sel[0])["values"][1]
        if messagebox.askyesno("Confirmar",
                f"¿Eliminar usuario '{nombre}'?"):
            try:
                eliminar_usuario(uid)
                self._cargar_usuarios()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

# ════════════════════════════════════════════════════════
#  PESTAÑA: CAMPAÑAS
# ════════════════════════════════════════════════════════
    def _crear_pestaña_campanas(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚔️ Campañas")

        # ── Formulario ──
        form = ttk.LabelFrame(frame, text="Nueva campaña")
        form.pack(fill="x", padx=15, pady=10)

        ttk.Label(form, text="Nombre:").grid(
            row=0, column=0, padx=(15,5), pady=10, sticky="e")
        self.entry_camp_nombre = ttk.Entry(form, width=25)
        self.entry_camp_nombre.grid(row=0, column=1, padx=(0,15), pady=10)

        ttk.Label(form, text="Descripción:").grid(
            row=0, column=2, padx=(15,5), pady=10, sticky="e")
        self.entry_camp_desc = ttk.Entry(form, width=30)
        self.entry_camp_desc.grid(row=0, column=3, padx=(0,15), pady=10)

        ttk.Label(form, text="Master (usuario):").grid(
            row=0, column=4, padx=(15,5), pady=10, sticky="e")
        self.combo_master = ttk.Combobox(form, width=18, state="readonly")
        self.combo_master.grid(row=0, column=5, padx=(0,15), pady=10)

        ttk.Button(form, text="Crear campaña",
            command=self._crear_campana).grid(
            row=0, column=6, padx=15, pady=10)

        # ── Tabla ──
        cols = ("ID", "Nombre", "Estado", "Fecha")
        self.tabla_camp = ttk.Treeview(frame, columns=cols,
            show="headings", height=10)
        self.tabla_camp.heading("ID",     text="ID")
        self.tabla_camp.heading("Nombre", text="Nombre")
        self.tabla_camp.heading("Estado", text="Estado")
        self.tabla_camp.heading("Fecha",  text="Fecha creación")
        self.tabla_camp.column("ID",     width=260)
        self.tabla_camp.column("Nombre", width=200)
        self.tabla_camp.column("Estado", width=100)
        self.tabla_camp.column("Fecha",  width=180)
        self.tabla_camp.pack(fill="both", expand=True, padx=15, pady=(0,5))

        # ── Botones ──
        bar = ttk.Frame(frame)
        bar.pack(fill="x", padx=15, pady=(0,10))
        ttk.Button(bar, text="🔄 Actualizar",
            command=self._cargar_campanas).pack(side="left", padx=5)
        ttk.Button(bar, text="👥 Ver miembros",
            command=self._ver_miembros).pack(side="left", padx=5)

        self._cargar_campanas()
        self._cargar_combo_masters()

    def _cargar_combo_masters(self):
        usuarios = obtener_usuarios() or []
        self._usuarios_lista = usuarios
        self.combo_master["values"] = [
            u["nombre_usuario"] for u in usuarios]
        if usuarios:
            self.combo_master.current(0)

    def _crear_campana(self):
        nombre = self.entry_camp_nombre.get().strip()
        desc   = self.entry_camp_desc.get().strip()
        if not nombre:
            messagebox.showwarning("Campo vacío", "Escribe un nombre.")
            return
        idx       = self.combo_master.current()
        master_id = self._usuarios_lista[idx]["id"] if idx >= 0 else None
        try:
            crear_campana(nombre, desc, master_id=master_id)
            messagebox.showinfo("Éxito", f"Campaña '{nombre}' creada.")
            self.entry_camp_nombre.delete(0, tk.END)
            self.entry_camp_desc.delete(0, tk.END)
            self._cargar_campanas()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _cargar_campanas(self):
        for row in self.tabla_camp.get_children():
            self.tabla_camp.delete(row)
        for c in (obtener_campanas() or []):
            self.tabla_camp.insert("", "end", values=(
                c["id"], c["nombre"],
                c["estado"], c["fecha_creacion"]))

    def _ver_miembros(self):
        sel = self.tabla_camp.selection()
        if not sel:
            messagebox.showwarning("Sin selección",
                "Selecciona una campaña.")
            return
        cid    = self.tabla_camp.item(sel[0])["values"][0]
        nombre = self.tabla_camp.item(sel[0])["values"][1]
        from app.modelos.campanas import obtener_campana_por_id
        campana = obtener_campana_por_id(cid)
        if not campana or not campana.get("miembros"):
            messagebox.showinfo("Miembros",
                "Esta campaña no tiene miembros.")
            return
        texto = "\n".join(
            f"  • {m['nombre_usuario']} ({m['rol']})"
            for m in campana["miembros"])
        messagebox.showinfo(f"Miembros de '{nombre}'", texto)

# ════════════════════════════════════════════════════════
#  PESTAÑA: PERSONAJES
# ════════════════════════════════════════════════════════
    def _crear_pestaña_personajes(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🧙 Personajes")

        # ── Formulario ──
        form = ttk.LabelFrame(frame, text="Nuevo personaje")
        form.pack(fill="x", padx=15, pady=10)

        labels = ["Nombre:", "Raza:", "Clase:"]
        self.entry_per = {}
        for i, label in enumerate(labels):
            ttk.Label(form, text=label).grid(
                row=0, column=i*2, padx=(15,5), pady=10, sticky="e")
            entry = ttk.Entry(form, width=18)
            entry.grid(row=0, column=i*2+1, padx=(0,10), pady=10)
            self.entry_per[label.replace(":","").lower()] = entry

        ttk.Label(form, text="Campaña:").grid(
            row=0, column=6, padx=(10,5), pady=10, sticky="e")
        self.combo_camp_per = ttk.Combobox(form, width=18, state="readonly")
        self.combo_camp_per.grid(row=0, column=7, padx=(0,10), pady=10)

        ttk.Label(form, text="Jugador:").grid(
            row=0, column=8, padx=(10,5), pady=10, sticky="e")
        self.combo_jugador = ttk.Combobox(form, width=18, state="readonly")
        self.combo_jugador.grid(row=0, column=9, padx=(0,10), pady=10)

        ttk.Button(form, text="Crear personaje",
            command=self._crear_personaje).grid(
            row=0, column=10, padx=15, pady=10)

        # ── Tabla ──
        cols = ("ID", "Nombre", "Raza", "Clase", "Nivel", "Jugador")
        self.tabla_per = ttk.Treeview(frame, columns=cols,
            show="headings", height=10)
        anchos = [260, 160, 120, 120, 60, 140]
        for col, ancho in zip(cols, anchos):
            self.tabla_per.heading(col, text=col)
            self.tabla_per.column(col, width=ancho)
        self.tabla_per.pack(fill="both", expand=True, padx=15, pady=(0,5))

        # ── Botones ──
        bar = ttk.Frame(frame)
        bar.pack(fill="x", padx=15, pady=(0,10))
        ttk.Button(bar, text="🔄 Cargar personajes de campaña",
            command=self._cargar_personajes).pack(side="left", padx=5)
        ttk.Button(bar, text="📋 Ver ficha completa",
            command=self._ver_ficha).pack(side="left", padx=5)
        ttk.Button(bar, text="✏️ Editar estadísticas",
            command=self._editar_estadisticas).pack(side="left", padx=5)

        self._cargar_combos_personajes()
        self._cargar_personajes()

    def _cargar_combos_personajes(self):
        campanas = obtener_campanas() or []
        usuarios = obtener_usuarios() or []
        self._campanas_lista = campanas
        self._jugadores_lista = usuarios
        self.combo_camp_per["values"] = [c["nombre"] for c in campanas]
        self.combo_jugador["values"]  = [u["nombre_usuario"] for u in usuarios]
        if campanas: self.combo_camp_per.current(0)
        if usuarios: self.combo_jugador.current(0)

    def _crear_personaje(self):
        nombre = self.entry_per["nombre"].get().strip()
        raza   = self.entry_per["raza"].get().strip()
        clase  = self.entry_per["clase"].get().strip()
        ic = self.combo_camp_per.current()
        iu = self.combo_jugador.current()
        if not nombre or ic < 0 or iu < 0:
            messagebox.showwarning("Campos vacíos",
                "Rellena nombre, campaña y jugador.")
            return
        cid = self._campanas_lista[ic]["id"]
        uid = self._jugadores_lista[iu]["id"]
        try:
            crear_personaje(cid, uid, nombre, raza, clase)
            messagebox.showinfo("Éxito", f"Personaje '{nombre}' creado.")
            for e in self.entry_per.values():
                e.delete(0, tk.END)
            self._cargar_personajes()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _cargar_personajes(self):
        for row in self.tabla_per.get_children():
            self.tabla_per.delete(row)
        ic = self.combo_camp_per.current()
        if ic < 0:
            return
        cid = self._campanas_lista[ic]["id"]
        for p in (obtener_personajes_de_campana(cid) or []):
            self.tabla_per.insert("", "end", values=(
                p["id"], p["nombre"], p["raza"],
                p["clase"], p["nivel"], p["jugador"]))

    def _ver_ficha(self):
        sel = self.tabla_per.selection()
        if not sel:
            messagebox.showwarning("Sin selección",
                "Selecciona un personaje.")
            return
        pid = self.tabla_per.item(sel[0])["values"][0]
        p   = obtener_personaje_completo(pid)
        if not p:
            return
        texto = (
            f"Nombre:  {p['nombre']}  |  Raza: {p['raza']}  "
            f"|  Clase: {p['clase']}\n"
            f"Nivel:   {p['nivel']}  |  EXP: {p['experiencia']}\n\n"
            f"── Estadísticas ──────────────────\n"
            f"  FUE {p['fuerza']}  DES {p['destreza']}  "
            f"CON {p['constitucion']}\n"
            f"  INT {p['inteligencia']}  SAB {p['sabiduria']}  "
            f"CAR {p['carisma']}\n"
            f"  Vida: {p['vida_actual']} / {p['vida_max']}\n\n"
            f"── Inventario ────────────────────\n"
        )
        if p["inventario"]:
            for obj in p["inventario"]:
                texto += f"  • {obj['nombre_objeto']} x{obj['cantidad']}\n"
        else:
            texto += "  (vacío)\n"
        messagebox.showinfo(f"Ficha de {p['nombre']}", texto)

    def _editar_estadisticas(self):
        sel = self.tabla_per.selection()
        if not sel:
            messagebox.showwarning("Sin selección",
                "Selecciona un personaje.")
            return
        pid  = self.tabla_per.item(sel[0])["values"][0]
        p    = obtener_personaje_completo(pid)
        if not p:
            return
        # Ventana secundaria para editar stats
        win = tk.Toplevel(self.root)
        win.title(f"Estadísticas — {p['nombre']}")
        win.configure(bg=self.colors["bg"])
        win.geometry("340x380")
        win.resizable(False, False)

        stats = ["fuerza","destreza","constitucion",
                 "inteligencia","sabiduria","carisma",
                 "vida_max","vida_actual"]
        entries = {}
        for i, stat in enumerate(stats):
            ttk.Label(win, text=stat.capitalize()+":").grid(
                row=i, column=0, padx=20, pady=6, sticky="e")
            e = ttk.Entry(win, width=8)
            e.insert(0, str(p[stat]))
            e.grid(row=i, column=1, padx=10, pady=6, sticky="w")
            entries[stat] = e

        def guardar():
            try:
                valores = {k: int(v.get()) for k, v in entries.items()}
                actualizar_estadisticas(pid, **valores)
                messagebox.showinfo("Guardado",
                    "Estadísticas actualizadas.")
                win.destroy()
            except ValueError:
                messagebox.showerror("Error",
                    "Todos los valores deben ser números enteros.")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        ttk.Button(win, text="💾 Guardar cambios",
            command=guardar).grid(
            row=len(stats), column=0, columnspan=2, pady=15)