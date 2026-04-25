"""
Basic connection and measurement example for the Rigol DSA815.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Rigol_DSA815 import DSA815

sa = DSA815()
sa.conn()

print("Identity:", sa.identify())

sa.set_input_atten(10)
sa.set_center_frequency(100e6)  # 100 MHz
sa.set_span(20e6)               # 20 MHz span
sa.set_RBW(30e3)                # 30 kHz RBW
sa.set_VBW(30e3)

sa.initiate_measurement()

freqs, amps = sa.get_sweep_data()
print(f"Sweep: {freqs[0]/1e6:.3f} - {freqs[-1]/1e6:.3f} MHz, {len(freqs)} points")
print(f"Peak amplitude: {max(amps):.1f} dBm at {freqs[amps.argmax()]/1e6:.3f} MHz")

sa.dis()
