# test_tkinter.py
import tkinter as tk

print("Attempting to create a Tkinter window...")

try:
    root = tk.Tk()
    root.title("Tkinter Test")
    root.geometry("200x100+300+300")
    label = tk.Label(root, text="Window is visible!")
    label.pack(pady=20, padx=20)
    print("Window created successfully. Starting mainloop.")
    root.mainloop()
except Exception as e:
    print(f"\nAn error occurred: {e}")
    input("Press Enter to exit.")