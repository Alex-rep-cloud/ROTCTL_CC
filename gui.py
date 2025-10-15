import tkinter as tk
from tkinter import ttk
import threading
import time
from rotctl import *

class RotatorGUI(tk.Tk):
    def __init__(self, model=1, device="/dev/ttyUSB0"):
        super().__init__()
        self.title("ROTCTL Control Center")
        self.geometry("600x200")
        self.resizable(False, False)

        self.rot = ROTCTL(model=model, device=device)

        self.az_var = tk.DoubleVar(value=0.0)
        self.el_var = tk.DoubleVar(value=0.0)

        self._build_ui()

        self._running = True
        threading.Thread(target=self._update_loop, daemon=True).start()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill="both", expand=True)

        left = ttk.Frame(frm)
        left.grid(row=0, column=0, sticky="nsew")

        ttk.Label(left, text="Azimuth (°)", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.az_entry = ttk.Entry(left, textvariable=self.az_var, width=10)
        self.az_entry.grid(row=0, column=1, sticky="w", padx=5)
        self.az_label = ttk.Label(left, text="Lecture: 0.0°", font=("Arial", 10))
        self.az_label.grid(row=0, column=2, padx=10)

        ttk.Label(left, text="Élévation (°)", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=(10, 5))
        self.el_entry = ttk.Entry(left, textvariable=self.el_var, width=10)
        self.el_entry.grid(row=1, column=1, sticky="w", padx=5)
        self.el_label = ttk.Label(left, text="Lecture: 0.0°", font=("Arial", 10))
        self.el_label.grid(row=1, column=2, padx=10)

        ttk.Button(left, text="Envoyer position", command=lambda: self.rot.set_pos(self.az_var.get(), self.el_var.get())).grid(row=2, column=0, columnspan=3, pady=20, sticky="ew")

        right = ttk.Frame(frm)
        right.grid(row=0, column=1, padx=20, sticky="nsew")

        speed = 5.0
        ttk.Button(right, text="↑", width=5, command=lambda: self.rot.move(ROTCTL.UP, speed)).grid(row=0, column=1, pady=5)
        ttk.Button(right, text="←", width=5, command=lambda: self.rot.move(ROTCTL.LEFT, speed)).grid(row=1, column=0, padx=5)
        ttk.Button(right, text="Stop", width=5, command=self.rot.stop).grid(row=1, column=1, pady=5)
        ttk.Button(right, text="→", width=5, command=lambda: self.rot.move(ROTCTL.RIGHT, speed)).grid(row=1, column=2, padx=5)
        ttk.Button(right, text="↓", width=5, command=lambda: self.rot.move(ROTCTL.DOWN, speed)).grid(row=2, column=1, pady=5)

    def _update_loop(self):
        while self._running:
            try:
                az, el = tools.parse_pos(self.rot.get_pos())

                self.after(0, self._update_display, az, el)
            except Exception:
                pass
            time.sleep(1.0)

    def _update_display(self, az, el):
        self.az_label.config(text=f"{az:.1f}°")
        self.el_label.config(text=f"{el:.1f}°")

    def on_close(self):
        self._running = False
        try:
            self.rot.close()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    app = RotatorGUI(model=1, device="/dev/tty.usbserial-XXXXX")
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
