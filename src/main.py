import numpy as np
import pyvisa
import time

class DSA815(object):
    def __init__(self):
        self.inst = None

    def conn(self):
        # Initialize the VISA resource manager
        rm = pyvisa.ResourceManager()
        
        # List all connected devices
        devices = rm.list_resources()
        print("Connected devices:", devices)
        
        # Connect to the Rigol DSA-815 (replace with your device's USB address)
        self.inst = rm.open_resource('USB0::0x1AB1::0x0960::DSA8B214600696::INSTR')
        
        # Set a longer timeout (e.g., 10 seconds)
        self.inst.timeout = 10000
        
        # Check connection
        print(self.inst.query('*IDN?'))
    
    def dis(self):
        if self.inst:
            self.inst.close()
            self.inst = None

    def identify(self):
        """
        Return identify string, which has serial number
        
        Returns:
            (string) Identity of the instrument
            ex: Rigol Technologies,DSA815,DSA8A134700016,00.01.12.00.02
        """
        return self.inst.query("*IDN?")

    #########################
    ###### Settings #########
    #########################
    
    def TG_enable(self, state):
        """
        Turn the tracking generator on or off.
        
        Args:
            state (True/False): true if the tracking generator will be turned on
        """
        tstate = "1" if state else "0"
        self.inst.write(f":OUTput:STATe {tstate}")

    def set_TG_amp(self, amp):
        """
        Set the TG output amplitude power in dBm
        
        Args:
            amp (number): the output power, from -40 dBm to 0 dBm.
            
        Raises:
            ValueError: if the amplitude is outside of the range [-40, 0]
        """
        if amp > 0 or amp < -40:
            raise ValueError("Amplitude outside of allowed range -40dBm to 0dBm")
        self.inst.write(f":SOURce:POWer:LEVel:IMMediate:AMPLitude {amp}")
        # Print the set value
        set_amp = self.inst.query(":SOURce:POWer:LEVel:IMMediate:AMPLitude?")
        print(f"TG Amplitude set to: {set_amp} dBm")

    def get_TG_amp(self):
        """
        Get the TG output amplitude power in dBm
        
        Returns:
            float: The current TG output amplitude in dBm
        """
        amp = self.inst.query(":SOURce:POWer:LEVel:IMMediate:AMPLitude?")
        return float(amp)

    def set_freq_limits(self, f_low, f_hi):
        """
        Set the frequency range on the spectrum analyzer.
        
        Args:
            f_low: The minimum frequency to scan
            f_hi: The maximum frequency
        
        Raises:
            ValueError: if the frequency is outside of the range [0, 3.2 GHz]
        """
        if f_low < 0 or f_low > 3.2e9 or f_hi < 0 or f_hi > 3.2e9:
            raise ValueError("Frequencies must be between 0 Hz and 3.2 GHz")
        self.inst.write(f":SENSe:FREQuency:STARt {f_low}")
        self.inst.write(f":SENSe:FREQuency:STOP {f_hi}")
        
        # Print the set values
        start_freq = self.inst.query(":SENSe:FREQuency:STARt?")
        stop_freq = self.inst.query(":SENSe:FREQuency:STOP?")
        print(f"Start Frequency set to: {start_freq} Hz")
        print(f"Stop Frequency set to: {stop_freq} Hz")

    def set_RBW(self, RBW):
        """
        Set the resolution bandwidth.
        
        Args:
            RBW: The new resolution bandwidth, in the range 10 Hz to 1 MHz in 1-3-10 steps
        """
        if RBW < 10 or RBW > 1e6:
            raise ValueError("RBW must be between 10 Hz and 1 MHz")
        self.inst.write(f":SENSe:BANDwidth:RESolution {RBW}")
        # Print the set value
        set_RBW = self.inst.query(":SENSe:BANDwidth:RESolution?")
        print(f"Resolution Bandwidth set to: {set_RBW} Hz")

    def get_RBW(self):
        """
        Get the current resolution bandwidth.
        
        Returns:
            float: The current resolution bandwidth in Hz
        """
        RBW = self.inst.query(":SENSe:BANDwidth:RESolution?")
        return float(RBW)

    def set_center_frequency(self, freq):
        """
        Set the center frequency.
        
        Args:
            freq (float): The center frequency in Hz, must be between 0 Hz and 3.2 GHz
        
        Raises:
            ValueError: if the frequency is outside of the range [0, 3.2 GHz]
        """
        if freq < 0 or freq > 3.2e9:
            raise ValueError("Frequency must be between 0 Hz and 3.2 GHz")
        self.inst.write(f":SENSe:FREQuency:CENTer {freq}")
        # Print the set value
        set_freq = self.inst.query(":SENSe:FREQuency:CENTer?")
        print(f"Center Frequency set to: {set_freq} Hz")

    def get_center_frequency(self):
        """
        Query the center frequency.
        
        Returns:
            float: The center frequency in Hz
        """
        freq = self.inst.query(":SENSe:FREQuency:CENTer?")
        return float(freq)

    def set_span(self, span):
        """
        Set the frequency span.
        
        Args:
            span (float): The frequency span in Hz, must be between 0 Hz and 3.2 GHz
        
        Raises:
            ValueError: if the span is outside of the range [0, 3.2 GHz]
        """
        if span < 0 or span > 3.2e9:
            raise ValueError("Span must be between 0 Hz and 3.2 GHz")
        self.inst.write(f":SENSe:FREQuency:SPAN {span}")
        # Print the set value
        set_span = self.inst.query(":SENSe:FREQuency:SPAN?")
        print(f"Frequency Span set to: {set_span} Hz")

    def get_span(self):
        """
        Query the frequency span.
        
        Returns:
            float: The frequency span in Hz
        """
        span = self.inst.query(":SENSe:FREQuency:SPAN?")
        return float(span)

    def set_VBW(self, VBW):
        """
        Set the video bandwidth.
        
        Args:
            VBW: The new video bandwidth, in the range 1 Hz to 3 MHz
        
        Raises:
            ValueError: if the VBW is outside of the range [1 Hz, 3 MHz]
        """
        if VBW < 1 or VBW > 3e6:
            raise ValueError("VBW must be between 1 Hz and 3 MHz")
        self.inst.write(f":SENSe:BANDwidth:VIDeo {VBW}")
        # Print the set value
        set_VBW = self.inst.query(":SENSe:BANDwidth:VIDeo?")
        print(f"Video Bandwidth set to: {set_VBW} Hz")

    def get_VBW(self):
        """
        Get the current video bandwidth.
        
        Returns:
            int: The current video bandwidth in Hz
        """
        VBW = self.inst.query(":SENSe:BANDwidth:VIDeo?")
        return int(VBW)

    def enable_RF(self, state):
        """
        Turn the RF preamp on or off.
        
        Args:
            state: True to enable the preamp
        """
        state_s = "1" if state else "0"
        self.inst.write(f":SENSe:POWer:RF:GAIN:STATe {state_s}")
        
        # Query the status to confirm
        current_state = self.inst.query(":SENSe:POWer:RF:GAIN:STATe?")
        print(f"RF preamp is {'enabled' if current_state.strip() == '1' else 'disabled'}")

    def set_input_atten(self, atten):
        """
        Set the value of the input attenuation, in dB.
        
        Args:
            atten (integer): The new attenuation, in the range [0, 30] dB.
        
        Raises:
            ValueError: if the attenuation level is not in the range [0, 30]
            TypeError: if the attenuation level is not an integer
        """
        if atten < 0 or atten > 30:
            raise ValueError("Input attenuation must be between 0 and 30 dB")
        if not isinstance(atten, int):
            raise TypeError("Attenuation level must be an integer")
        
        self.inst.write(f":SENSe:POWer:RF:ATTenuation {atten}")
        current_atten = self.inst.query(":SENSe:POWer:RF:ATTenuation?")
        print(f"Attenuator is set to: {current_atten} dB")

    def get_input_atten(self):
        """
        Get the current value of the input attenuation.
        
        Returns:
            int: The current attenuation in dB
        """
        current_atten = self.inst.query(":SENSe:POWer:RF:ATTenuation?")
        return int(current_atten)

    #########################
    #### Initiate Subsystem ##
    #########################

    def initiate_measurement(self):
        """
        Initiate a single sweep or measurement.
        """
        # Ensure the instrument is in single measurement mode
        self.inst.write(":INITiate:CONTinuous OFF")
        
        # Initiate the measurement
        self.inst.write(":INITiate:IMMediate")
        
        # Wait until the measurement is complete
        while (int(self.inst.query(":STATus:OPERation:CONDition?")) & (1 << 3)):
            pass
        
        print("Measurement initiated and completed.")

    ##############
    ### Trace ####
    ##############

    def set_trace_mode(self, trace_num, mode):
        """
        Set the type of the specified trace.
        
        Args:
            trace_num (int): The trace number (1, 2, or 3)
            mode (str): The mode to set (WRITe, MAXHold, MINHold, VIEW, BLANk, VIDeoavg, POWeravg)
        
        Raises:
            ValueError: if the trace number or mode is invalid
        """
        valid_modes = ["WRITe", "MAXHold", "MINHold", "VIEW", "BLANk", "VIDeoavg", "POWeravg"]
        if trace_num not in [1, 2, 3]:
            raise ValueError("Trace number must be 1, 2, or 3")
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode. Valid modes are: {', '.join(valid_modes)}")
        
        self.inst.write(f":TRACe{trace_num}:MODE {mode}")
        # Print the set value
        set_mode = self.inst.query(f":TRACe{trace_num}:MODE?")
        print(f"Trace {trace_num} mode set to: {set_mode.strip()}")

    def get_trace_mode(self, trace_num):
        """
        Query the type of the specified trace.
        
        Args:
            trace_num (int): The trace number (1, 2, or 3)
        
        Returns:
            str: The current mode of the specified trace
        
        Raises:
            ValueError: if the trace number is invalid
        """
        if trace_num not in [1, 2, 3]:
            raise ValueError("Trace number must be 1, 2, or 3")
        
        mode = self.inst.query(f":TRACe{trace_num}:MODE?")
        return mode.strip()
    
    #############
    ### Sweep ###
    #############

    def set_sweep_time(self, sweep_time):
        """
        Set the sweep time.
        
        Args:
            sweep_time (float): The sweep time in seconds, must be between 20 us and 3200 s
        
        Raises:
            ValueError: if the sweep time is outside of the range [20 us, 3200 s]
        """
        if sweep_time < 20e-6 or sweep_time > 3200:
            raise ValueError("Sweep time must be between 20 us and 3200 s")
        self.inst.write(f":SENSe:SWEep:TIME {sweep_time}")
        # Print the set value
        set_sweep_time = self.inst.query(":SENSe:SWEep:TIME?")
        print(f"Sweep time set to: {set_sweep_time} s")

    def get_sweep_time(self):
        """
        Query the sweep time.
        
        Returns:
            float: The sweep time in seconds
        """
        sweep_time = self.inst.query(":SENSe:SWEep:TIME?")
        return float(sweep_time)
    
    def set_sweep_count(self, count):
        """
        Set the number of sweeps for a single sweep.
        
        Args:
            count (int): The number of sweeps, must be between 1 and 9999
        
        Raises:
            ValueError: if the count is outside of the range [1, 9999]
        """
        if count < 1 or count > 9999:
            raise ValueError("Sweep count must be between 1 and 9999")
        self.inst.write(f":SENSe:SWEep:COUNt {count}")
        # Print the set value
        set_count = self.inst.query(":SENSe:SWEep:COUNt?")
        print(f"Sweep count set to: {set_count}")

    def get_sweep_count(self):
        """
        Query the number of sweeps for a single sweep.
        
        Returns:
            int: The number of sweeps
        """
        count = self.inst.query(":SENSe:SWEep:COUNt?")
        return int(count)

    #########################
    ######## FORMAT #########
    #########################

    def set_format(self, data_format):
        """
        Set the data format for trace data.
        
        Args:
            data_format (str): The data format to set (ASCii or REAL[,32])
        
        Raises:
            ValueError: if the data format is invalid
        """
        valid_formats = ["ASCii", "REAL,32"]
        if data_format not in valid_formats:
            raise ValueError(f"Invalid data format. Valid formats are: {', '.join(valid_formats)}")
        
        self.inst.write(f":FORMat:TRACe:DATA {data_format}")
        print(f"Data format set to: {data_format}")

    def get_format(self):
        """
        Query the current data format for trace data.
        
        Returns:
            str: The current data format (ASCii or REAL[,32])
        """
        data_format = self.inst.query(":FORMat:TRACe:DATA?")
        return data_format.strip()
    
    #########################
    #### Initiate Subsystem ##
    #########################

    def initiate_measurement(self):
        """
        Initiate a single sweep or measurement.
        """
        # Ensure the instrument is in single measurement mode
        self.inst.write(":INITiate:CONTinuous OFF")
        
        # Initiate the measurement
        self.inst.write(":INITiate:IMMediate")
        
        # Wait until the measurement is complete
        while (int(self.inst.query(":STATus:OPERation:CONDition?")) & (1 << 3)):
            pass
        
        print("Measurement initiated and completed.")


    #########################
    ######## MMEMory ########
    #########################

    def delete_file(self, file_name):
        """
        Delete the specified file from the instrument's memory.
        
        Args:
            file_name (str): The file name with path to delete (e.g., E:\\Rigol\\Trace1.trc)
        """
        self.inst.write(f":MMEMory:DELete {file_name}")
        print(f"File {file_name} deleted")

    def get_disk_info(self):
        """
        Get information about the disk.
        
        Returns:
            dict: Disk information including name, type, file system, space used, and total capacity
        """
        info_str = self.inst.query(":MMEMory:DISK:INFormation?")
        info_lines = info_str.split('\n')
        info_dict = {}
        for line in info_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                info_dict[key.strip()] = value.strip()
        return info_dict


    def load_setup(self, file_name):
        """
        Load a setup from the specified file.
        
        Args:
            file_name (str): The file name with path to load the setup (e.g., D:\\Setup1.set)
        """
        self.inst.write(f":MMEMory:LOAD:SETUp {file_name}")
        print(f"Setup loaded from {file_name}")

    def load_state(self, file_name):
        """
        Load a state from the specified file.
        
        Args:
            file_name (str): The file name with path to load the state (e.g., D:\\state.sta)
        """
        self.inst.write(f":MMEMory:LOAD:STATe {file_name}")
        print(f"State loaded from {file_name}")

    ##### Store ####

    def get_disk_info(self):
        """
        Get information about the disk.
        
        Returns:
            dict: Disk information including name, type, file system, space used, and total capacity
        """
        info_str = self.inst.query(":MMEMory:DISK:INFormation?")
        info_lines = info_str.split('\n')
        info_dict = {}
        for line in info_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                info_dict[key.strip()] = value.strip()
        return info_dict

    def save_results_to_USB(self, file_name):
        """
        Save the current measurement results to the specified file.
        
        Args:
            file_name (str): The file name with path to save the results (e.g., E:\\Results.csv)
        """
        self.inst.write(f":MMEMory:STORe:RESults {file_name}")
        print(f"Measurement results saved to {file_name}")
    
    
    def save_trace(self, trace_label, file_name):
        """
        Save the specified trace with the specified filename.
        
        Args:
            trace_label (str): The trace label (TRACE1, TRACE2, TRACE3, MATH, ALL)
            file_name (str): The file name with path to save the trace (e.g., D:\\Trace1.trc)
        
        Raises:
            ValueError: if the trace label is invalid
        """
        valid_labels = ["TRACE1", "TRACE2", "TRACE3", "MATH", "ALL"]
        if trace_label not in valid_labels:
            raise ValueError(f"Invalid trace label. Valid labels are: {', '.join(valid_labels)}")
        
        self.inst.write(f":MMEMory:STORe:TRACe {trace_label},{file_name}")
        print(f"Trace {trace_label} saved to {file_name}")


    def load_trace(self, file_name, save_path):
        """
        Load the specified trace file (.trc) from the spectrum analyzer and save it to a file on the computer.
        
        Args:
            file_name (str): The file name with path to load the trace (e.g., D:\\Trace1.trc)
            save_path (str): The file path to save the trace data on the computer (e.g., D:\\trace1.csv)
        
        Raises:
            FileNotFoundError: if the specified file does not exist
        """
        try:
            # Load the trace file from the spectrum analyzer
            self.inst.write(f":MMEMory:LOAD:TRACe {file_name}")
            print(f"Trace loaded from {file_name}")
            
            # Read the trace data
            data = self.inst.query(":TRACe:DATA? TRACE1")
            
            # Save the data to a CSV file
            with open(save_path, 'w') as file:
                file.write(data)
            print(f"Trace data saved to {save_path}")
        except pyvisa.errors.VisaIOError:
            raise FileNotFoundError(f"The file {file_name} does not exist.")

    def save_screenshot(self, file_name):
        """
        Save the current screen image to the specified file.
        
        Args:
            file_name (str): The file name with path to save the screenshot (e.g., E:\\screen.bmp)
        """
        self.inst.write(f":MMEMory:STORe:SCReen {file_name}")
        print(f"Screenshot saved to {file_name}")

    def save_setup(self, file_name):
        """
        Save the current setup to the specified file.
        
        Args:
            file_name (str): The file name with path to save the setup (e.g., D:\\Setup1.set)
        """
        self.inst.write(f":MMEMory:STORe:SETUp {file_name}")
        print(f"Setup saved to {file_name}")

    def save_state(self, file_name):
        """
        Save the current instrument state to the specified file.
        
        Args:
            file_name (str): The file name with path to save the state (e.g., D:\\state.sta)
        """
        self.inst.write(f":MMEMory:STORe:STATe 1,{file_name}")
        print(f"Instrument state saved to {file_name}")

    #####################
    ###  Measurements ###
    #####################

    def measure_trace(self):
        """
        Measure a single trace from the spectrum analyzer.
        
        Returns:
            List of amplitudes in dBm at each frequency measured
        """
        # Turn off continuous tracing
        self.inst.write(":INITiate:CONTinuous OFF")
        
        # Set up trace 1 to be read as ASCII
        self.inst.write(":TRACe1:MODE WRITe")
        self.inst.write(":FORMat:TRACe:DATA ASCii")
        
        # Trigger once
        self.inst.write(":INITiate")
        # Wait until done
        while (int(self.inst.query(":STATus:OPERation:CONDition?")) & (1 << 3)):
            pass
            pass
        
        # Ask for data and process it
        dataString = self.inst.query(":TRACe:DATA? TRACE1")
        dataList = dataString.split(", ")
        dataList[0] = dataList[0].split()[1]
        amplitudes = [float(i) for i in dataList]

        return amplitudes

    def get_sweep_data(self):
        """
        Retrieve the current sweep data, including start frequency, stop frequency, and all points of the spectrum.
        
        Returns:
            Tuple of (frequencies, amplitudes)
        """
        # Get the start and stop frequencies
        start_freq = float(self.inst.query(':SENSe:FREQuency:STARt?'))
        time.sleep(0.1)  # Add a small delay
        stop_freq = float(self.inst.query(':SENSe:FREQuency:STOP?'))
        time.sleep(0.1)  # Add a small delay
        
        # Get the number of points
        num_points = int(self.inst.query(':SENSe:SWEep:POINts?'))
        time.sleep(0.1)  # Add a small delay
        
        # Send a command to the spectrum analyzer to get trace data
        dataString = self.inst.query(":TRACe:DATA? TRACE1")
        time.sleep(0.1)  # Add a small delay
        
        # Read the data
        data = self.inst.read()
        
        # Convert the data to a numpy array
        data = np.array(data.split(','), dtype=float)
        
        # Generate the frequency array
        freq = np.linspace(start_freq, stop_freq, num_points)
        
        return freq, data

