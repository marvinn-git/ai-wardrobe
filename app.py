import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("AI Wardrobe (Desktop)")
root.geometry("800x500")

title = ttk.Label(root, text="AI Wardrobe (Desktop)", font=("Arial", 18))
title.pack(pady=20)

info = ttk.Label(root, text="Si ves esta ventana, la app de escritorio funciona ✅")
info.pack(pady=10)

btn = ttk.Button(root, text="Botón de prueba", command=lambda: info.config(text="Click detectado ✅"))
btn.pack(pady=10)

root.mainloop()
