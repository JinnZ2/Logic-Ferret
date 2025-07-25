

import tkinter as tk
from tkinter import filedialog, scrolledtext
from sensor_suite.sensors.fallacy_overlay import annotate_text

def run_analysis():
    raw_text = input_box.get("1.0", tk.END)
    annotated, counts = annotate_text(raw_text)

    # Show annotated transcript
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, annotated)

    # Show fallacy counts
    count_box.delete("1.0", tk.END)
    for k, v in counts.items():
        count_box.insert(tk.END, f"{k}: {v}\n")

def load_file():
    file_path = filedialog.askopenfilename()
    with open(file_path, "r") as f:
        input_box.delete("1.0", tk.END)
        input_box.insert(tk.END, f.read())

root = tk.Tk()
root.title("🧠 Logic Ferret GUI – Fallacy Hunter 9000")
root.geometry("1200x700")
root.configure(bg="#1e1e1e")

# Input Text
tk.Label(root, text="Input Transcript", fg="#ffffff", bg="#1e1e1e").pack()
input_box = scrolledtext.ScrolledText(root, height=10, width=150, wrap=tk.WORD, bg="#2e2e2e", fg="#dcdcdc")
input_box.pack(padx=10, pady=5)

# Buttons
button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack()

tk.Button(button_frame, text="Load File", command=load_file, bg="#3e3e3e", fg="white").pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="🧪 FLAG BULLSHIT", command=run_analysis, bg="#a00000", fg="white").pack(side=tk.LEFT, padx=5)

# Output
tk.Label(root, text="Annotated Transcript", fg="#ffffff", bg="#1e1e1e").pack()
output_box = scrolledtext.ScrolledText(root, height=15, width=150, wrap=tk.WORD, bg="#2e2e2e", fg="#dcdcdc")
output_box.pack(padx=10, pady=5)

# Fallacy Breakdown
tk.Label(root, text="Fallacy Counts", fg="#ffffff", bg="#1e1e1e").pack()
count_box = scrolledtext.ScrolledText(root, height=5, width=50, bg="#2e2e2e", fg="#00ff99")
count_box.pack(padx=10, pady=5)

root.mainloop()



cd logic-monk-stack/gui
python fallacy_gui.py
