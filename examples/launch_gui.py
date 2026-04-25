"""
Launch the PyQt5 spectrum viewer.

With optional peak-lock detection: set lock_freq_Hz to the frequency you want
to monitor (Hz). The lock indicator turns green when the peak inside the
detection window exceeds lock_threshold_dBm.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5 import QtWidgets
from Rigol_GUI import SpectrumViewer

app = QtWidgets.QApplication(sys.argv)

# No lock detection (default):
viewer = SpectrumViewer()

# With lock detection at 70 MHz, +-5 kHz window, -40 dBm threshold:
# viewer = SpectrumViewer(lock_freq_Hz=70e6, lock_bw_Hz=5e3, lock_threshold_dBm=-40)

viewer.show()
sys.exit(app.exec_())
