import tkinter as tk
from tkinter import ttk, filedialog, messagebox

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
        for F in (HomeScreen, WardrobeScreen, OutfitsScreen, InspoScreen):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show("HomeScreen")

    def show(self, frame_name: str):
        self.frames[frame_name].tkraise()
        # refrescar si hace falta
        if frame_name == "WardrobeScreen":
            self.frames[frame_name].refresh()
        if frame_name == "OutfitsScreen":
            self.frames[frame_name].refresh()


class HomeScreen(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        title = ttk.Label(self, text="AI Wardrobe", font=("Arial", 22))
        title.pack(pady=(10, 20))

        subtitle = ttk.Label(self, text="Esqueleto de pantallas (sin login / sin DB todavía)")
        subtitle.pack(pady=(0, 25))

        btn_frame = ttk.Frame(self)
        btn_frame.pack()

        big_style = {"width": 25}

        ttk.Button(btn_frame, text="Abrir Armario", command=lambda: controller.show("WardrobeScreen"), **big_style).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(btn_frame, text="Outfits", command=lambda: controller.show("OutfitsScreen"), **big_style).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(btn_frame, text="Get Inspo", command=lambda: controller.show("InspoScreen"), **big_style).grid(row=0, column=2, padx=10, pady=10)


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

        # Lista
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=(10, 0))

        self.listbox = tk.Listbox(body, height=18)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=scrollbar.set)

        self.hint = ttk.Label(self, text="(Vacío) Añade ropa para verla aquí.")
        self.hint.pack(pady=10)

    def refresh(self):
        self.listbox.delete(0, tk.END)

        selected_filter = self.filter_var.get()
        items = WARDROBE_ITEMS

        if selected_filter != "Todas":
            items = [it for it in items if selected_filter in it.get("categories", [])]

        if not items:
            self.hint.configure(text="(Vacío) Añade ropa para verla aquí.")
        else:
            self.hint.configure(text="")

        for idx, it in enumerate(items):
            cats = ", ".join(it.get("categories", []))
            tags = ", ".join(it.get("tags", [])) if it.get("tags") else "-"
            name = it.get("name", "Sin nombre")
            self.listbox.insert(tk.END, f"{name}  |  {cats}  |  Tags: {tags}")

    def open_add_dialog(self):
        AddItemDialog(self, on_save=self.add_item)

    def add_item(self, item: dict):
        WARDROBE_ITEMS.append(item)
        self.refresh()

    def delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Borrar", "Selecciona una prenda primero.")
            return

        # OJO: como filtramos, el index de listbox no siempre coincide con WARDROBE_ITEMS.
        # Para el esqueleto, lo hacemos simple: borrado por nombre+cats (suficiente por ahora).
        line = self.listbox.get(sel[0])
        name = line.split("|")[0].strip()

        for i, it in enumerate(WARDROBE_ITEMS):
            if it.get("name") == name:
                del WARDROBE_ITEMS[i]
                break

        self.refresh()


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
