import tkinter as tk
from tkinter import ttk
from rotctl import *

# Create a rotctl instance
rotor = ROTCTL()

def dumb(*args):
    pass

def move_btn(dir):
    if dir == "UP":
        rotor.move(ROTCTL.UP, 10)
    if dir == "DOWN":
        rotor.move(ROTCTL.DOWN, 10)
    if dir == "LEFT":
        rotor.move(ROTCTL.LEFT, 10)
    if dir == "RIGHT":
        rotor.move(ROTCTL.RIGHT, 10)
    print(rotor.get_pos())

# Create the main window
root = tk.Tk()
root.title("Simple GUI Example")
root.geometry("800x150")

# Configure grid layout
root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=2)
root.columnconfigure(2, weight=2)

# Left frame for labels and entries
left_frame = ttk.Frame(root, padding=10)
left_frame.grid(row=0, column=0, sticky="nsew")

# Right frame for buttons
right_frame = ttk.Frame(root, padding=10)
right_frame.grid(row=0, column=1, sticky="ns")

# Azimuth
label1 = ttk.Label(left_frame, text="Azimuth :")
label1.grid(row=0, column=0, sticky="w", pady=5)
entry1 = ttk.Entry(left_frame, width=25)
entry1.grid(row=0, column=1, pady=5)
btn = ttk.Button(left_frame, text="Send", command=lambda n="Send": dumb(n))
btn.grid(row=0, column=2, sticky="ew", pady=5)

# Elevation
label2 = ttk.Label(left_frame, text="Elevation :")
label2.grid(row=1, column=0, sticky="w", pady=5)
entry2 = ttk.Entry(left_frame, width=25)
entry2.grid(row=1, column=1, pady=5)
btn = ttk.Button(left_frame, text="Send", command=lambda n="Send": dumb(n))
btn.grid(row=1, column=2, sticky="ew", pady=5)

# 4 directions cardinales
btn = ttk.Button(right_frame, text="UP", command=lambda n="UP": move_btn(n))
btn.grid(row=0, column=1, sticky="ew", pady=5)
btn = ttk.Button(right_frame, text="LEFT", command=lambda n="LEFT": move_btn(n))
btn.grid(row=1, column=0, sticky="ew", pady=5)
btn = ttk.Button(right_frame, text="RIGHT", command=lambda n="RIGHT": move_btn(n))
btn.grid(row=1, column=2, sticky="ew", pady=5)
btn = ttk.Button(right_frame, text="DOWN", command=lambda n="DOWN": move_btn(n))
btn.grid(row=2, column=1, sticky="ew", pady=5)

# Run the GUI
root.mainloop()
