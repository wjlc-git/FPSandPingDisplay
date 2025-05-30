import tkinter as tk
from tkinter import colorchooser
import time
import threading
import subprocess
import platform

class DisplayTray:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.overrideredirect(True)  # Frameless
        self.window.geometry("+0+0")
        self.window.attributes('-topmost', True)
        self.window.configure(bg='black')

        self.label = tk.Label(self.window, text="", fg='lime', bg='black', font=("Consolas", 14), justify="left")
        self.label.pack(padx=10, pady=5)

        # Defaults
        self.show_fps = True
        self.show_ping = True
        self.text_color = 'lime'
        self.bg_color = 'black'
        self.font_size = 14

        # Movement
        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)

        # Stats
        self.last_time = time.time()
        self.fps = 0
        self.ping = 0

        self.update_stats()
        self.update_ping()

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.window.winfo_x() + event.x - self._x
        y = self.window.winfo_y() + event.y - self._y
        self.window.geometry(f"+{x}+{y}")

    def update_stats(self):
        now = time.time()
        self.fps = round(1 / (now - self.last_time), 1)
        self.last_time = now

        lines = []
        if self.show_fps:
            lines.append(f"FPS: {self.fps}")
        if self.show_ping:
            lines.append(f"Ping: {self.ping} ms")

        self.label.config(text="\n".join(lines), fg=self.text_color, bg=self.bg_color,
                          font=("Consolas", self.font_size))
        self.window.configure(bg=self.bg_color)
        self.window.after(1000 // 60, self.update_stats)

    def update_ping(self):
        def ping():
            try:
                param = '-n' if platform.system().lower() == 'windows' else '-c'
                output = subprocess.check_output(
                    ['ping', param, '1', 'google.com'],
                    stderr=subprocess.DEVNULL, universal_newlines=True
                )
                if 'time=' in output:
                    time_part = output.split('time=')[1].split(' ')[0]
                    self.ping = int(float(time_part.replace('ms', '').strip()))
            except Exception:
                self.ping = -1
            self.window.after(1000, self.update_ping)

        threading.Thread(target=ping, daemon=True).start()

class SettingsTray:
    def __init__(self, master, display_tray):
        self.display_tray = display_tray
        self.window = tk.Toplevel(master)
        self.window.title("wjlc quick info")
        self.window.geometry("250x200")

        # Font Size
        tk.Label(self.window, text="Font Size:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.font_spin = tk.Spinbox(self.window, from_=8, to=48, width=5, command=self.update_font_size)
        self.font_spin.delete(0, 'end')
        self.font_spin.insert(0, self.display_tray.font_size)
        self.font_spin.grid(row=0, column=1, sticky="w")

        # Text Color
        tk.Label(self.window, text="Text Color:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Button(self.window, text="Choose", command=self.choose_text_color).grid(row=1, column=1, sticky="w")

        # Background Color
        tk.Label(self.window, text="Background Color:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        tk.Button(self.window, text="Choose", command=self.choose_bg_color).grid(row=2, column=1, sticky="w")

        # Toggle FPS
        self.fps_var = tk.IntVar(value=int(display_tray.show_fps))
        tk.Checkbutton(self.window, text="Show FPS", variable=self.fps_var, command=self.toggle_fps).grid(row=3, column=0, sticky="w", padx=5)

        # Toggle Ping
        self.ping_var = tk.IntVar(value=int(display_tray.show_ping))
        tk.Checkbutton(self.window, text="Show Ping", variable=self.ping_var, command=self.toggle_ping).grid(row=4, column=0, sticky="w", padx=5)

    def update_font_size(self):
        try:
            self.display_tray.font_size = int(self.font_spin.get())
        except ValueError:
            pass

    def choose_text_color(self):
        color = colorchooser.askcolor(title="Choose Text Color")[1]
        if color:
            self.display_tray.text_color = color

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.display_tray.bg_color = color

    def toggle_fps(self):
        self.display_tray.show_fps = bool(self.fps_var.get())

    def toggle_ping(self):
        self.display_tray.show_ping = bool(self.ping_var.get())

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide root window

    display = DisplayTray(root)
    settings = SettingsTray(root, display)

    root.mainloop()
