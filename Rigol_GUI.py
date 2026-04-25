"""
Rigol DSA815 - Standalone PyQt5 spectrum viewer.

Run directly:
    python Rigol_GUI.py

Or import and embed as a widget:
    from Rigol_GUI import SpectrumViewer
"""
import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

try:
    from .Rigol_DSA815 import DSA815
except ImportError:
    from Rigol_DSA815 import DSA815


class SpectrumViewer(QtWidgets.QMainWindow):
    """
    Live spectrum display for the Rigol DSA815.

    Optional peak-lock detection: supply lock_freq_Hz to enable the
    lock indicator. The indicator turns green when the peak power
    inside [lock_freq_Hz - lock_bw_Hz, lock_freq_Hz + lock_bw_Hz]
    exceeds lock_threshold_dBm.

    Args:
        lock_freq_Hz (float | None): Center frequency for lock detection in Hz.
            None disables the feature entirely.
        lock_bw_Hz (float): Half-bandwidth of the detection window in Hz.
        lock_threshold_dBm (float): Minimum peak power to declare lock (dBm).
        update_interval_ms (int): Plot refresh interval in milliseconds.
    """

    def __init__(
        self,
        lock_freq_Hz=None,
        lock_bw_Hz=5e3,
        lock_threshold_dBm=-40,
        update_interval_ms=100,
    ):
        super().__init__()
        self.setWindowTitle("Rigol DSA815 Live Spectrum")
        self.resize(1200, 700)

        self.lock_freq_Hz = lock_freq_Hz
        self.lock_bw_Hz = lock_bw_Hz
        self.lock_threshold_dBm = lock_threshold_dBm
        self.locked = False

        self.sa = DSA815()
        self.sa.conn()
        self.sa.inst.write(":FORMat:TRACe:DATA REAL,32")
        self.points = int(self.sa.inst.query(':SENSe:SWEep:POINts?'))
        self._update_frequency_range()

        self._build_ui()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update_plot)
        self.timer.start(update_interval_ms)

    # ─── UI construction ────────────────────────────────────────────────────

    def _build_ui(self):
        self.plot_widget = pg.PlotWidget()
        self.curve = self.plot_widget.plot(pen='y')
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_widget.setLabel('left', 'Amplitude', units='dBm')
        self.plot_widget.showGrid(x=True, y=True)

        control_panel = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()

        self.center_freq_input = QtWidgets.QLineEdit(str(self.f_center / 1e6))
        layout.addRow("Center Freq (MHz):", self.center_freq_input)

        self.span_input = QtWidgets.QLineEdit(str(self.span / 1e6))
        layout.addRow("Span (MHz):", self.span_input)

        self.rbw_input = QtWidgets.QLineEdit("10000")
        layout.addRow("RBW (Hz):", self.rbw_input)

        apply_btn = QtWidgets.QPushButton("Apply Settings")
        apply_btn.clicked.connect(self._apply_settings)
        layout.addWidget(apply_btn)

        single_btn = QtWidgets.QPushButton("Single Sweep")
        single_btn.clicked.connect(self._single_sweep)
        layout.addWidget(single_btn)

        cont_btn = QtWidgets.QPushButton("Continuous Sweep")
        cont_btn.clicked.connect(self._continuous_sweep)
        layout.addWidget(cont_btn)

        self.toggle_button = QtWidgets.QPushButton("Pause Updates")
        self.toggle_button.setCheckable(True)
        self.toggle_button.toggled.connect(self._toggle_updates)
        layout.addWidget(self.toggle_button)

        save_btn = QtWidgets.QPushButton("Save Trace to CSV")
        save_btn.clicked.connect(self._save_trace)
        layout.addWidget(save_btn)

        control_panel.setLayout(layout)

        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()

        # Lock status bar (only shown when lock detection is configured)
        if self.lock_freq_Hz is not None:
            status_bar = QtWidgets.QHBoxLayout()
            self.lock_led = QtWidgets.QLabel()
            self.lock_led.setFixedSize(20, 20)
            self.lock_led.setStyleSheet("background-color: red; border-radius: 10px;")
            self.lock_label = QtWidgets.QLabel("Beat Note Lock Status: UNLOCKED")
            self.lock_label.setStyleSheet("color: red; font-weight: bold; font-size: 16pt;")
            self.lock_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            status_bar.addWidget(self.lock_led)
            status_bar.addWidget(self.lock_label)
            status_bar.addStretch()
            main_layout.addLayout(status_bar)

        row = QtWidgets.QHBoxLayout()
        row.addWidget(self.plot_widget, stretch=4)
        row.addWidget(control_panel, stretch=1)
        main_layout.addLayout(row)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    # ─── Helpers ────────────────────────────────────────────────────────────

    def _update_frequency_range(self):
        self.f_start = float(self.sa.inst.query(':SENSe:FREQuency:STARt?'))
        self.f_stop  = float(self.sa.inst.query(':SENSe:FREQuency:STOP?'))
        self.span    = self.f_stop - self.f_start
        self.f_center = (self.f_stop + self.f_start) / 2
        self.frequencies = np.linspace(self.f_start, self.f_stop, self.points)

    def _apply_settings(self):
        try:
            f_center = float(self.center_freq_input.text()) * 1e6
            span     = float(self.span_input.text()) * 1e6
            rbw      = float(self.rbw_input.text())
            self.sa.set_center_frequency(f_center)
            self.sa.set_span(span)
            self.sa.set_RBW(rbw)
            self._update_frequency_range()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def _single_sweep(self):
        try:
            self.sa.inst.write(":INITiate:CONTinuous OFF")
            self.sa.inst.write(":INITiate:IMMediate")
            while int(self.sa.inst.query(":STATus:OPERation:CONDition?")) & (1 << 3):
                QtWidgets.QApplication.processEvents()
            raw = self.sa.inst.query_binary_values(
                ":TRACe:DATA? TRACE1", datatype='f', container=np.array
            )
            self.curve.setData(self.frequencies, raw)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def _continuous_sweep(self):
        try:
            self.sa.inst.write(":INITiate:CONTinuous ON")
            if not self.timer.isActive():
                self.timer.start()
            self.toggle_button.setChecked(False)
            self.toggle_button.setText("Pause Updates")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def _toggle_updates(self, checked):
        if checked:
            self.timer.stop()
            self.toggle_button.setText("Resume Updates")
        else:
            self.timer.start()
            self.toggle_button.setText("Pause Updates")

    def _save_trace(self):
        try:
            raw = self.sa.inst.query_binary_values(
                ":TRACe:DATA? TRACE1", datatype='f', container=np.array
            )
            self._update_frequency_range()
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save Trace", "", "CSV Files (*.csv)"
            )
            if not path:
                return
            with open(path, 'w') as f:
                f.write("Frequency (Hz),Amplitude (dBm)\n")
                for freq, amp in zip(self.frequencies, raw):
                    f.write(f"{freq},{amp}\n")
            QtWidgets.QMessageBox.information(self, "Saved", f"Trace saved to:\n{path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def _update_plot(self):
        try:
            raw = self.sa.inst.query_binary_values(
                ":TRACe:DATA? TRACE1", datatype='f', container=np.array
            )
            self.curve.setData(self.frequencies, raw)

            if self.lock_freq_Hz is not None:
                idx = np.where(
                    (self.frequencies >= self.lock_freq_Hz - self.lock_bw_Hz) &
                    (self.frequencies <= self.lock_freq_Hz + self.lock_bw_Hz)
                )[0]
                self.locked = (
                    len(idx) > 0 and np.max(raw[idx]) > self.lock_threshold_dBm
                )
                if self.locked:
                    self.lock_label.setText("Beat Note Lock Status: LOCKED")
                    self.lock_label.setStyleSheet("color: green; font-weight: bold; font-size: 16pt;")
                    self.lock_led.setStyleSheet("background-color: green; border-radius: 10px;")
                else:
                    self.lock_label.setText("Beat Note Lock Status: UNLOCKED")
                    self.lock_label.setStyleSheet("color: red; font-weight: bold; font-size: 16pt;")
                    self.lock_led.setStyleSheet("background-color: red; border-radius: 10px;")

        except Exception as e:
            print(f"[SpectrumViewer] update error: {e}")

    def closeEvent(self, event):
        self.timer.stop()
        self.sa.dis()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    viewer = SpectrumViewer()
    viewer.show()
    sys.exit(app.exec_())
