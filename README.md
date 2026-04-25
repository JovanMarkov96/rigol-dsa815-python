# rigol-dsa815-control

Python driver and GUI for the **Rigol DSA815** spectrum analyzer (0 Hz – 1.5 GHz / 3.2 GHz).

Control the instrument over USB or LAN via PyVISA. Includes a live spectrum viewer (PyQt5 and Tkinter variants) with optional peak-lock detection.

> **Trademark notice:** Rigol and DSA815 are trademarks of RIGOL Technologies Co., Ltd. This project is not affiliated with or endorsed by RIGOL.

---

## Requirements

- Python 3.8+
- [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) or [pyvisa-py](https://pyvisa.readthedocs.io/projects/pyvisa-py/) backend
- See `requirements.txt` for Python packages

```
pip install -r requirements.txt
```

---

## Quick start

```python
from Rigol_DSA815 import DSA815

sa = DSA815()
sa.conn()                          # auto-detect over USB/LAN
sa.set_center_frequency(100e6)    # 100 MHz center
sa.set_span(10e6)                  # 10 MHz span
sa.set_RBW(10e3)                   # 10 kHz RBW
freqs, amps = sa.get_sweep_data()  # returns (np.ndarray, np.ndarray)
sa.dis()
```

---

## Launch GUI

### PyQt5 (recommended)

```bash
python Rigol_GUI.py
```

Or embed with optional peak-lock detection:

```python
from Rigol_GUI import SpectrumViewer
from PyQt5 import QtWidgets
import sys

app = QtWidgets.QApplication(sys.argv)
# lock_freq_Hz=None disables lock indicator (default)
viewer = SpectrumViewer(lock_freq_Hz=100e6, lock_bw_Hz=5e3, lock_threshold_dBm=-40)
viewer.show()
sys.exit(app.exec_())
```

### Tkinter

```bash
python Rigol_TK_viewer.py
```

---

## API overview

### Connection

| Method | Description |
|--------|-------------|
| `conn()` | Auto-detect and connect (USB or LAN) |
| `dis()` | Disconnect and release VISA resource |
| `identify()` | Return IDN string |

### Frequency

| Method | Description |
|--------|-------------|
| `set_center_frequency(freq)` | Set center frequency (Hz) |
| `set_span(span)` | Set span (Hz) |
| `set_freq_limits(f_low, f_hi)` | Set start/stop frequency (Hz) |
| `get_center_frequency()` | Read center frequency (Hz) |
| `get_span()` | Read span (Hz) |

### Bandwidth

| Method | Description |
|--------|-------------|
| `set_RBW(rbw)` | Set resolution bandwidth (Hz) |
| `set_VBW(vbw)` | Set video bandwidth (Hz) |
| `get_RBW()` / `get_VBW()` | Read current bandwidth settings |

### Sweep

| Method | Description |
|--------|-------------|
| `set_sweep_time(t)` | Set sweep time (s) |
| `set_sweep_count(n)` | Set number of sweeps per acquisition |
| `initiate_measurement()` | Trigger single sweep, block until done |

### Trace and data

| Method | Description |
|--------|-------------|
| `measure_trace()` | Single sweep, returns list of amplitudes (dBm) |
| `get_sweep_data()` | Current sweep, returns (frequencies, amplitudes) as numpy arrays |
| `set_trace_mode(n, mode)` | Set trace 1-3 display mode |
| `set_format(fmt)` | Set transfer format: 'ASCii' or 'REAL,32' |

### Input / RF

| Method | Description |
|--------|-------------|
| `set_input_atten(dB)` | Set input attenuation 0-30 dB |
| `enable_RF(state)` | Enable/disable RF preamplifier |
| `TG_enable(state)` | Enable/disable tracking generator |
| `set_TG_amp(dBm)` | Set TG output power -40 to 0 dBm |

### Storage (MMEMory)

| Method | Description |
|--------|-------------|
| `save_trace(label, path)` | Save trace to instrument storage |
| `load_trace(path, csv_path)` | Load trace from instrument, save as CSV |
| `save_screenshot(path)` | Capture screen to instrument storage |
| `save_setup(path)` / `load_setup(path)` | Save/load instrument configuration |
| `get_disk_info()` | Return dict of instrument disk information |

---

## Examples

See the [`examples/`](examples/) directory:

- `examples/basic_connection.py` — connect, configure, read a trace
- `examples/launch_gui.py` — launch the PyQt5 viewer with custom lock detection

---

## License

MIT License. See [LICENSE](LICENSE).
