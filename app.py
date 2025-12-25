import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from auth import register_user, login_user
import session

# -------------------------
# Estado temporal en memoria (sin DB aún)
# -------------------------
WARDROBE_ITEMS = []  # cada item: dict con name, categories(list), tags(list), photos(list)

DEFAULT_CATEGORIES = [
    "Camiseta", "Pantalón", "Sudadera", "Shorts", "Zapatillas", "Chaqueta", "Accesorio"
]

# -------------------------
# App / Navegación por pantallas (Frames)
# -------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Wardrobe (Skeleton)")
        self.geometry("900x550")

        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (AuthScreen, HomeScreen, WardrobeScreen, OutfitsScreen, InspoScreen):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show("AuthScreen")

    def show(self, frame_name: str):
        self.frames[frame_name].tkraise()
        if frame_name == "HomeScreen":
            self.frames[frame_name].refresh_user()
        if frame_name == "WardrobeScreen":
            self.frames[frame_name].refresh()
        if frame_name == "OutfitsScreen":
            self.frames[frame_name].refresh()
        


class AuthScreen(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="AI Wardrobe", font=("Arial", 22)).pack(pady=(20, 10))
        ttk.Label(self, text="Login / Register (MongoDB)", foreground="gray").pack(pady=(0, 20))

        form = ttk.Frame(self, padding=12)
        form.pack()

        ttk.Label(form, text="Email").grid(row=0, column=0, sticky="w")
        self.email_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.email_var, width=35).grid(row=1, column=0, pady=(4, 12))

        ttk.Label(form, text="Password").grid(row=2, column=0, sticky="w")
        self.pass_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.pass_var, show="*", width=35).grid(row=3, column=0, pady=(4, 12))

        btns = ttk.Frame(self)
        btns.pack(pady=10)

        ttk.Button(btns, text="Login", command=self.do_login, width=18).grid(row=0, column=0, padx=8)
        ttk.Button(btns, text="Register", command=self.do_register, width=18).grid(row=0, column=1, padx=8)

        self.msg = ttk.Label(self, text="", foreground="red")
        self.msg.pack(pady=10)

    def do_login(self):
        email = self.email_var.get().strip()
        password = self.pass_var.get().strip()
        if not email or not password:
            self.msg.config(text="Email y password son obligatorios.")
            return

        uid, err = login_user(email, password)
        if err:
            self.msg.config(text=err)
            return

        session.current_user_id = uid
        session.current_user_email = email.lower()
        self.msg.config(text="")
        self.controller.show("HomeScreen")

    def do_register(self):
        email = self.email_var.get().strip()
        password = self.pass_var.get().strip()
        if not email or not password:
            self.msg.config(text="Email y password son obligatorios.")
            return

        uid, err = register_user(email, password)
        if err:
            self.msg.config(text=err)
            return

        session.current_user_id = uid
        session.current_user_email = email.lower()
        self.msg.config(text="")
        self.controller.show("HomeScreen")


class HomeScreen(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        title = ttk.Label(self, text="AI Wardrobe", font=("Arial", 22))
        title.pack(pady=(10, 20))

        subtitle = ttk.Label(self, text="Esqueleto de pantallas (sin login / sin DB todavía)")
        subtitle.pack(pady=(0, 25))

        self.user_label = ttk.Label(self, text="Usuario: (no logueado)")
        self.user_label.pack(pady=(0, 20))


        btn_frame = ttk.Frame(self)
        btn_frame.pack()

        big_style = {"width": 25}

        ttk.Button(btn_frame, text="Abrir Armario", command=lambda: controller.show("WardrobeScreen"), **big_style).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(btn_frame, text="Outfits", command=lambda: controller.show("OutfitsScreen"), **big_style).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(btn_frame, text="Get Inspo", command=lambda: controller.show("InspoScreen"), **big_style).grid(row=0, column=2, padx=10, pady=10)

    def refresh_user(self):
        if session.current_user_email:
            self.user_label.config(text=f"Usuario: {session.current_user_email}")
        else:
            self.user_label.config(text="Usuario: (no logueado)")    



class WardrobeScreen(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        top = ttk.Frame(self)
        top.pack(fill="x")

        ttk.Button(top, text="← Home", command=lambda: controller.show("HomeScreen")).pack(side="left")
        ttk.Label(top, text="Armario", font=("Arial", 18)).pack(side="left", padx=12)

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(15, 10))

        ttk.Button(actions, text="Añadir ropa", command=self.open_add_dialog).pack(side="left")
        ttk.Button(actions, text="Borrar seleccionada", command=self.delete_selected).pack(side="left", padx=8)

        # Filtro simple por categoría (UI solamente)
        ttk.Label(actions, text="Filtro:").pack(side="left", padx=(20, 6))
        self.filter_var = tk.StringVar(value="Todas")
        self.filter_combo = ttk.Combobox(actions, textvariable=self.filter_var, state="readonly",
                                         values=["Todas"] + DEFAULT_CATEGORIES)
        self.filter_combo.pack(side="left")
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # --- Scrollable area (secciones + grid) ---
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, pady=(10, 0))

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        def on_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        def on_canvas_resize(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.inner.bind("<Configure>", on_configure)
        self.canvas.bind("<Configure>", on_canvas_resize)

        self.hint = ttk.Label(self, text="(Vacío) Añade ropa para verla aquí.")
        self.hint.pack(pady=10)

    def refresh(self):
        # limpiar contenido anterior
        if hasattr(self, "inner"):
            for child in self.inner.winfo_children():
                child.destroy()

        selected_filter = self.filter_var.get()
        items = WARDROBE_ITEMS

        if selected_filter != "Todas":
            items = [it for it in items if selected_filter in it.get("categories", [])]

        if not items:
            self.hint.configure(text="(Vacío) Añade ropa para verla aquí.")
            return
        else:
            self.hint.configure(text="")

        # Agrupar por primera categoría (simple por ahora)
        grouped = {}
        for it in items:
            cat = it.get("categories", ["Sin categoría"])[0]
            grouped.setdefault(cat, []).append(it)

        # Crear secciones + grid
        for cat, cat_items in grouped.items():
            section = ttk.LabelFrame(self.inner, text=cat, padding=10)
            section.pack(fill="x", padx=8, pady=8)

            cols = 3
            for i, it in enumerate(cat_items):
                card = ttk.Frame(section, padding=10, relief="solid")
                r = i // cols
                c = i % cols
                card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

                name = it.get("name", "Sin nombre")
                ttk.Label(card, text=name, font=("Arial", 11)).pack()

                ttk.Label(card, text="(imagen pronto)", foreground="gray").pack(pady=(6, 0))

            for c in range(cols):
                section.columnconfigure(c, weight=1)

    
    def open_add_dialog(self):
        AddItemDialog(self, on_save=self.add_item)

    def add_item(self, item: dict):
        WARDROBE_ITEMS.append(item)
        self.refresh()

    def delete_selected(self):
        messagebox.showinfo("Borrar", "En el siguiente paso haremos selección por click en cards.")
   


class OutfitsScreen(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        top = ttk.Frame(self)
        top.pack(fill="x")

        ttk.Button(top, text="← Home", command=lambda: controller.show("HomeScreen")).pack(side="left")
        ttk.Label(top, text="Outfits", font=("Arial", 18)).pack(side="left", padx=12)

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(15, 10))

        ttk.Button(actions, text="Crear nuevo outfit (placeholder)", command=self.placeholder).pack(side="left")
        ttk.Button(actions, text="Borrar outfit (placeholder)", command=self.placeholder).pack(side="left", padx=8)

        self.listbox = tk.Listbox(self, height=18)
        self.listbox.pack(fill="both", expand=True, pady=(10, 0))

        self.empty = ttk.Label(self, text="(Vacío) Aquí aparecerán outfits guardados/favoritos.")
        self.empty.pack(pady=10)

    def refresh(self):
        # Por ahora siempre vacío
        self.listbox.delete(0, tk.END)
        self.empty.configure(text="(Vacío) Aquí aparecerán outfits guardados/favoritos.")

    def placeholder(self):
        messagebox.showinfo("Outfits", "Under construction 🚧")


class InspoScreen(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        top = ttk.Frame(self)
        top.pack(fill="x")

        ttk.Button(top, text="← Home", command=lambda: controller.show("HomeScreen")).pack(side="left")
        ttk.Label(top, text="Get Inspo", font=("Arial", 18)).pack(side="left", padx=12)

        big = ttk.Label(self, text="Under construction 🚧", font=("Arial", 22))
        big.pack(pady=80)

        small = ttk.Label(self, text="Aquí luego irá Pinterest / inspiración por gustos / búsquedas.")
        small.pack()


class AddItemDialog(tk.Toplevel):
    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.title("Añadir ropa")
        self.geometry("520x520")
        self.resizable(False, False)
        self.on_save = on_save
        self.photos = []  # placeholder

        wrapper = ttk.Frame(self, padding=12)
        wrapper.pack(fill="both", expand=True)

        ttk.Label(wrapper, text="Nombre de la prenda").pack(anchor="w")
        self.name_var = tk.StringVar()
        ttk.Entry(wrapper, textvariable=self.name_var).pack(fill="x", pady=(0, 10))

        ttk.Label(wrapper, text="Categorías (puedes marcar varias)").pack(anchor="w")

        self.cat_vars = {}
        cats_box = ttk.Frame(wrapper)
        cats_box.pack(fill="x", pady=(6, 10))

        # Checkboxes en 2 columnas
        for i, cat in enumerate(DEFAULT_CATEGORIES):
            v = tk.BooleanVar(value=False)
            self.cat_vars[cat] = v
            r = i // 2
            c = i % 2
            ttk.Checkbutton(cats_box, text=cat, variable=v).grid(row=r, column=c, sticky="w", padx=(0, 20), pady=2)

        ttk.Label(wrapper, text="Añadir categoría personalizada (opcional)").pack(anchor="w", pady=(10, 0))
        self.custom_cat_var = tk.StringVar()
        ttk.Entry(wrapper, textvariable=self.custom_cat_var).pack(fill="x", pady=(6, 10))

        ttk.Label(wrapper, text="Tags (opcional, separados por coma)").pack(anchor="w")
        self.tags_var = tk.StringVar()
        ttk.Entry(wrapper, textvariable=self.tags_var).pack(fill="x", pady=(6, 10))

        ttk.Label(wrapper, text="Fotos (placeholder por ahora)").pack(anchor="w")
        ttk.Button(wrapper, text="Seleccionar fotos…", command=self.pick_photos).pack(anchor="w", pady=(6, 10))
        self.photos_label = ttk.Label(wrapper, text="0 fotos seleccionadas")
        self.photos_label.pack(anchor="w")

        btns = ttk.Frame(wrapper)
        btns.pack(fill="x", pady=(20, 0))

        ttk.Button(btns, text="Cancelar", command=self.destroy).pack(side="right")
        ttk.Button(btns, text="Guardar", command=self.save).pack(side="right", padx=8)

    def pick_photos(self):
        paths = filedialog.askopenfilenames(
            title="Selecciona fotos",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if paths:
            self.photos = list(paths)
            self.photos_label.configure(text=f"{len(self.photos)} fotos seleccionadas")

    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return

        categories = [cat for cat, var in self.cat_vars.items() if var.get()]
        custom = self.custom_cat_var.get().strip()
        if custom:
            categories.append(custom)

        if not categories:
            messagebox.showerror("Error", "Selecciona al menos una categoría (o añade una personalizada).")
            return

        tags_raw = self.tags_var.get().strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

        item = {
            "name": name,
            "categories": categories,
            "tags": tags,
            "photos": self.photos,  # placeholder (luego copiaremos a /images y guardaremos en Mongo)
        }

        self.on_save(item)
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
