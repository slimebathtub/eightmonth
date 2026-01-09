import tkinter as tk
from tkinter import ttk

class MilestoneList(tk.Frame):
    def __init__(self, master, milestones, on_toggle):
        super().__init__(master)
        self.on_toggle = on_toggle
        self.vars = []
        for m in milestones:
            var = tk.BooleanVar(value=m.done)
            cb = ttk.Checkbutton(self, text=m.title, variable=var, command=lambda mid=m.id, v=var: self.on_toggle(mid, v.get()))
            cb.pack(anchor='w', pady=2)
            self.vars.append(var)
