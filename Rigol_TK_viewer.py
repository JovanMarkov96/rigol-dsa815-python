"""
Rigol DSA815 - Standalone Tkinter spectrum viewer.

Run directly:
    python Rigol_TK_viewer.py
"""
import tkinter as tk
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import threading
import time

try:
    from .Rigol_DSA815 import DSA815
except ImportError:
    from Rigol_DSA815 import DSA815


class RigolTkViewer:
    """
    Tkinter-based live spectrum viewer for the Rigol DSA815.

    Args:
        master: Tk root window.
        lock_freq_Hz (float | None): Center frequency for beat-note lock detection in Hz.
            None disables the lock indicator.
        lock_bw_Hz (float): Half-bandwidth of the detection window in Hz.
        lock_threshold_dBm (float): Minimum peak power to declare lock (dBm).
        update_interval_s (float): Trace refresh interval in seconds.
    """

    def __init__(
        self,
        master,
        lock_freq_Hz=None,
        lock_bw_Hz=5e3,
        lock_threshold_dBm=-40,
        update_interval_s=0.2,
    ):
        self.master = master
        self.master.title("Rigol DSA815 Viewer")
        self.master.geometry("1000x600")

        self.lock_freq_Hz = lock_freq_Hz
        self.lock_bw_Hz = lock_bw_Hz
        self.lock_threshold_dBm = lock_threshold_dBm
        self.update_interval_s = update_interval_s
        self.locked = False

        self.sa = DSA815()
        try:
            self.sa.conn()
            self.sa.set_format("REAL,32")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to DSA815: {e}")
            return

        self.points = int(self.sa.inst.query(':SENSe:SWEep:POINts?'))
        self._update_frequency_range()
        self._build_ui()

        self.running = True
        threading.Thread(target=self._update_loop, daemon=True).start()

    # ─── UI ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        top = tk.Frame(self.master)
        top.pack(side=tk.TOP, fill=tk.X)

        if self.lock_freq_Hz is not None:
            self.lock_label = tk.Label(
                top, text="Beat Note Lock Status: UNLOCKED",
                font=("Arial", 14), fg="red"
            )
            self.lock_label.pack(side=tk.LEFT, padx=10, pady=5)
            self.lock_led = tk.Canvas(top, width=20, height=20)
            self.led_circle = self.lock_led.create_oval(2, 2, 18, 18, fill="red")
            self.lock_led.pack(side=tk.LEFT)

        fig = Figure(figsize=(8, 5), dpi=100)
        self.ax = fig.add_subplot(111, facecolor='black')
        self.line, = self.ax.plot([], [], color='yellow')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Amplitude (dBm)")
        self.ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.master)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas = canvas

    # ─── Helpers ────────────────────────────────────────────────────────────

    def _update_frequency_range(self):
        self.f_start = float(self.sa.inst.query(':SENSe:FREQuency:STARt?'))
        self.f_stop  = float(self.sa.inst.query(':SENSe:FREQuency:STOP?'))
        self.frequencies = np.linspace(self.f_start, self.f_stop, self.points)

    def _update_loop(self):
        while self.running:
            try:
                self._update_frequency_range()
                raw = self.sa.inst.query_binary_values(
                    ":TRACe:DATA? TRACE1", datatype='f', container=np.array
                )
                self.line.set_data(self.frequencies, raw)
                self.ax.set_xlim(self.frequencies[0], self.frequencies[-1])
                self.ax.set_ylim(min(raw) - 5, max(raw) + 5)
                self.canvas.draw()

                if self.lock_freq_Hz is not None:
                    idx = np.where(
                        (self.frequencies >= self.lock_freq_Hz - self.lock_bw_Hz) &
                        (self.frequencies <= self.lock_freq_Hz + self.lock_bw_Hz)
                    )[0]
                    self.locked = (
                        len(idx) > 0 and np.max(raw[idx]) > self.lock_threshold_dBm
                    )
                    if self.locked:
                        self.lock_label.config(
                            text="Beat Note Lock Status: LOCKED", fg="green"
                        )
                        self.lock_led.itemconfig(self.led_circle, fill="lightgreen")
                    else:
                        self.lock_label.config(
                            text="Beat Note Lock Status: UNLOCKED", fg="red"
                        )
                        self.lock_led.itemconfig(self.led_circle, fill="red")

            except Exception as e:
                print(f"[RigolTkViewer] update error: {e}")

            time.sleep(self.update_interval_s)

    def close(self):
        self.running = False
        self.sa.dis()
        self.master.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = RigolTkViewer(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
