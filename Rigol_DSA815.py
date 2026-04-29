import numpy as np
import pyvisa
import time


class DSA815(object):
    def __init__(self):
        self.inst = None
        self.rm = None

    def conn(self):
        """Auto-detect and connect to the first Rigol DSA815 found on any VISA interface."""
        self.rm = pyvisa.ResourceManager()
        devices = self.rm.list_resources()
        print("[Rigol] Detected VISA devices:", devices)
        for dev in devices:
            if dev.startswith("ASRL"):
                continue  # DSA815 connects via USB or LAN, never serial
            try:
                inst = self.rm.open_resource(dev)
                idn = inst.query("*IDN?")
                if "DSA815" in idn or "Rigol" in idn:
                    self.inst = inst
                    self.inst.timeout = 10000  # ms
                    print(f"[Rigol] Connected to: {dev} ({idn.strip()})")
                    return
                else:
                    inst.close()
            except Exception as e:
                print(f"[Rigol] Failed to connect to {dev}: {e}")
        raise IOError("[Rigol] DSA815 not found. Check USB/LAN connection.")

    def dis(self):
        if self.inst:
            self.inst.close()
            self.inst = None
        # Keep self.rm alive — closing a ResourceManager on NI-VISA can invalidate
        # sessions opened through other RMs in the same process.

    def identify(self):
        """
        Return the instrument identification string.

        Returns:
            str: e.g. 'Rigol Technologies,DSA815,DSA8A134700016,00.01.12.00.02'
        """
        return self.inst.query("*IDN?")

    # ─── Settings ────────────────────────────────────────────────────────────

    def TG_enable(self, state):
        """Turn the tracking generator on (True) or off (False)."""
        self.inst.write(f":OUTput:STATe {'1' if state else '0'}")

    def set_TG_amp(self, amp):
        """
        Set the TG output amplitude in dBm.

        Args:
            amp (float): Output power, range [-40, 0] dBm.
        """
        if amp > 0 or amp < -40:
            raise ValueError("Amplitude outside allowed range [-40, 0] dBm")
        self.inst.write(f":SOURce:POWer:LEVel:IMMediate:AMPLitude {amp}")

    def get_TG_amp(self):
        """Return current TG output amplitude in dBm."""
        return float(self.inst.query(":SOURce:POWer:LEVel:IMMediate:AMPLitude?"))

    def set_freq_limits(self, f_low, f_hi):
        """
        Set start and stop frequency of the sweep.

        Args:
            f_low (float): Start frequency in Hz, range [0, 3.2e9].
            f_hi  (float): Stop  frequency in Hz, range [0, 3.2e9].
        """
        if not (0 <= f_low <= 3.2e9) or not (0 <= f_hi <= 3.2e9):
            raise ValueError("Frequencies must be between 0 Hz and 3.2 GHz")
        self.inst.write(f":SENSe:FREQuency:STARt {f_low}")
        self.inst.write(f":SENSe:FREQuency:STOP {f_hi}")

    def set_center_frequency(self, freq):
        """
        Set center frequency.

        Args:
            freq (float): Center frequency in Hz, range [0, 3.2e9].
        """
        if not (0 <= freq <= 3.2e9):
            raise ValueError("Frequency must be between 0 Hz and 3.2 GHz")
        self.inst.write(f":SENSe:FREQuency:CENTer {freq}")

    def get_center_frequency(self):
        """Return current center frequency in Hz."""
        return float(self.inst.query(":SENSe:FREQuency:CENTer?"))

    def set_span(self, span):
        """
        Set frequency span.

        Args:
            span (float): Span in Hz, range [0, 3.2e9].
        """
        if not (0 <= span <= 3.2e9):
            raise ValueError("Span must be between 0 Hz and 3.2 GHz")
        self.inst.write(f":SENSe:FREQuency:SPAN {span}")

    def get_span(self):
        """Return current span in Hz."""
        return float(self.inst.query(":SENSe:FREQuency:SPAN?"))

    def set_RBW(self, RBW):
        """
        Set resolution bandwidth.

        Args:
            RBW (float): RBW in Hz, range [10, 1e6] in 1-3-10 steps.
        """
        if not (10 <= RBW <= 1e6):
            raise ValueError("RBW must be between 10 Hz and 1 MHz")
        self.inst.write(f":SENSe:BANDwidth:RESolution {RBW}")

    def get_RBW(self):
        """Return current RBW in Hz."""
        return float(self.inst.query(":SENSe:BANDwidth:RESolution?"))

    def set_VBW(self, VBW):
        """
        Set video bandwidth.

        Args:
            VBW (float): VBW in Hz, range [1, 3e6].
        """
        if not (1 <= VBW <= 3e6):
            raise ValueError("VBW must be between 1 Hz and 3 MHz")
        self.inst.write(f":SENSe:BANDwidth:VIDeo {VBW}")

    def get_VBW(self):
        """Return current VBW in Hz."""
        return int(self.inst.query(":SENSe:BANDwidth:VIDeo?"))

    def enable_RF(self, state):
        """Turn the RF preamplifier on (True) or off (False)."""
        self.inst.write(f":SENSe:POWer:RF:GAIN:STATe {'1' if state else '0'}")

    def set_input_atten(self, atten):
        """
        Set input attenuation.

        Args:
            atten (int): Attenuation in dB, range [0, 30].
        """
        if not (0 <= atten <= 30):
            raise ValueError("Input attenuation must be between 0 and 30 dB")
        if not isinstance(atten, int):
            raise TypeError("Attenuation must be an integer")
        self.inst.write(f":SENSe:POWer:RF:ATTenuation {atten}")

    def get_input_atten(self):
        """Return current input attenuation in dB."""
        return int(self.inst.query(":SENSe:POWer:RF:ATTenuation?"))

    # ─── Initiate ────────────────────────────────────────────────────────────

    def initiate_measurement(self):
        """Trigger a single sweep and block until it completes."""
        self.inst.write(":INITiate:CONTinuous OFF")
        self.inst.write(":INITiate:IMMediate")
        while int(self.inst.query(":STATus:OPERation:CONDition?")) & (1 << 3):
            pass

    # ─── Trace ───────────────────────────────────────────────────────────────

    def set_trace_mode(self, trace_num, mode):
        """
        Set trace display mode.

        Args:
            trace_num (int): Trace index 1-3.
            mode (str): One of WRITe, MAXHold, MINHold, VIEW, BLANk, VIDeoavg, POWeravg.
        """
        valid_modes = ["WRITe", "MAXHold", "MINHold", "VIEW", "BLANk", "VIDeoavg", "POWeravg"]
        if trace_num not in (1, 2, 3):
            raise ValueError("Trace number must be 1, 2, or 3")
        if mode not in valid_modes:
            raise ValueError(f"mode must be one of: {', '.join(valid_modes)}")
        self.inst.write(f":TRACe{trace_num}:MODE {mode}")

    def get_trace_mode(self, trace_num):
        """Return current mode string for the given trace."""
        if trace_num not in (1, 2, 3):
            raise ValueError("Trace number must be 1, 2, or 3")
        return self.inst.query(f":TRACe{trace_num}:MODE?").strip()

    # ─── Sweep ───────────────────────────────────────────────────────────────

    def set_sweep_time(self, sweep_time):
        """
        Set sweep time.

        Args:
            sweep_time (float): Sweep duration in seconds, range [20e-6, 3200].
        """
        if not (20e-6 <= sweep_time <= 3200):
            raise ValueError("Sweep time must be between 20 us and 3200 s")
        self.inst.write(f":SENSe:SWEep:TIME {sweep_time}")

    def get_sweep_time(self):
        """Return current sweep time in seconds."""
        return float(self.inst.query(":SENSe:SWEep:TIME?"))

    def set_sweep_count(self, count):
        """
        Set number of sweeps per acquisition.

        Args:
            count (int): Sweep count, range [1, 9999].
        """
        if not (1 <= count <= 9999):
            raise ValueError("Sweep count must be between 1 and 9999")
        self.inst.write(f":SENSe:SWEep:COUNt {count}")

    def get_sweep_count(self):
        """Return current sweep count."""
        return int(self.inst.query(":SENSe:SWEep:COUNt?"))

    # ─── Format ──────────────────────────────────────────────────────────────

    def set_format(self, data_format):
        """
        Set trace data output format.

        Args:
            data_format (str): 'ASCii' or 'REAL,32'.
        """
        valid = ["ASCii", "REAL,32"]
        if data_format not in valid:
            raise ValueError(f"data_format must be one of: {', '.join(valid)}")
        self.inst.write(f":FORMat:TRACe:DATA {data_format}")

    def get_format(self):
        """Return current trace data format string."""
        return self.inst.query(":FORMat:TRACe:DATA?").strip()

    # ─── Memory (MMEMory) ────────────────────────────────────────────────────

    def delete_file(self, file_name):
        """Delete a file from instrument storage."""
        self.inst.write(f":MMEMory:DELete {file_name}")

    def get_disk_info(self):
        """Return instrument disk info as a dict."""
        info_str = self.inst.query(":MMEMory:DISK:INFormation?")
        info_dict = {}
        for line in info_str.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info_dict[key.strip()] = value.strip()
        return info_dict

    def load_setup(self, file_name):
        """Load instrument setup from a file on instrument storage."""
        self.inst.write(f":MMEMory:LOAD:SETUp {file_name}")

    def load_state(self, file_name):
        """Load instrument state from a file on instrument storage."""
        self.inst.write(f":MMEMory:LOAD:STATe {file_name}")

    def save_results_to_USB(self, file_name):
        """Save current measurement results to a file on instrument storage."""
        self.inst.write(f":MMEMory:STORe:RESults {file_name}")

    def save_trace(self, trace_label, file_name):
        """
        Save a trace to instrument storage.

        Args:
            trace_label (str): TRACE1, TRACE2, TRACE3, MATH, or ALL.
            file_name   (str): Destination path on instrument.
        """
        valid_labels = ["TRACE1", "TRACE2", "TRACE3", "MATH", "ALL"]
        if trace_label not in valid_labels:
            raise ValueError(f"trace_label must be one of: {', '.join(valid_labels)}")
        self.inst.write(f":MMEMory:STORe:TRACe {trace_label},{file_name}")

    def load_trace(self, file_name, save_path):
        """
        Load a .trc file from instrument and save trace data as CSV on the PC.

        Args:
            file_name (str): Path on instrument.
            save_path (str): Local CSV path to write.
        """
        try:
            self.inst.write(f":MMEMory:LOAD:TRACe {file_name}")
            data = self.inst.query(":TRACe:DATA? TRACE1")
            with open(save_path, 'w') as f:
                f.write(data)
        except pyvisa.errors.VisaIOError:
            raise FileNotFoundError(f"File not found on instrument: {file_name}")

    def save_screenshot(self, file_name):
        """Save a screen capture to instrument storage."""
        self.inst.write(f":MMEMory:STORe:SCReen {file_name}")

    def save_setup(self, file_name):
        """Save current setup to instrument storage."""
        self.inst.write(f":MMEMory:STORe:SETUp {file_name}")

    def save_state(self, file_name):
        """Save current instrument state to instrument storage."""
        self.inst.write(f":MMEMory:STORe:STATe 1,{file_name}")

    # ─── Measurements ────────────────────────────────────────────────────────

    def measure_trace(self):
        """
        Acquire one single sweep (ASCII format) and return amplitude list.

        Returns:
            list[float]: Amplitudes in dBm for each sweep point.
        """
        self.inst.write(":INITiate:CONTinuous OFF")
        self.inst.write(":TRACe1:MODE WRITe")
        self.inst.write(":FORMat:TRACe:DATA ASCii")
        self.inst.write(":INITiate")
        while int(self.inst.query(":STATus:OPERation:CONDition?")) & (1 << 3):
            pass
        data_str = self.inst.query(":TRACe:DATA? TRACE1")
        parts = data_str.split(", ")
        parts[0] = parts[0].split()[1]
        return [float(x) for x in parts]

    def get_sweep_data(self):
        """
        Return (frequencies, amplitudes) for the current sweep using binary transfer.

        Returns:
            tuple[np.ndarray, np.ndarray]: Frequency array (Hz) and amplitude array (dBm).
        """
        start_freq = float(self.inst.query(':SENSe:FREQuency:STARt?'))
        stop_freq  = float(self.inst.query(':SENSe:FREQuency:STOP?'))
        num_points = int(self.inst.query(':SENSe:SWEep:POINts?'))
        self.inst.write(":FORMat:TRACe:DATA REAL,32")
        raw = self.inst.query_binary_values(":TRACe:DATA? TRACE1", datatype='f', container=np.array)
        freq = np.linspace(start_freq, stop_freq, num_points)
        return freq, raw
