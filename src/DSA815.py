from Rigol_DSA815 import DSA815

def main():
    # Connect to our spectrum analyzer
    print("Connecting...")
    test = DSA815()
    test.conn()  # Establish connection with the spectrum analyzer

    print("Configuring...")
    test.set_input_atten(30)  # Set input attenuation to 30 dB
    test.set_center_frequency(80e6)  # Set center frequency to 80 MHz
    test.set_span(130e3)  # Set frequency span to 130 kHz
    test.set_RBW(100)  # Set resolution bandwidth to 100 Hz
    test.set_VBW(100)  # Set video bandwidth to 100 Hz
    test.set_sweep_count(1)  # Set the number of sweeps to 1
    test.set_sweep_time(5)  # Set the sweep time to 5 seconds

    print("Initiating measurement...")
    test.initiate_measurement()  # Start the measurement process

    # Save the trace on the spectrum analyzer
    trace_file_save_path = 'D:\\Trace1.trc'
    test.save_trace('TRACE1', trace_file_save_path)  # Save the trace as 'TRACE1' to the specified path

    # Load the trace from the spectrum analyzer and save it to a CSV file on the computer
    csv_file_path = r'C:\\path\\to\\your\\directory\\trace1.csv'
    test.load_trace(trace_file_save_path, csv_file_path)  # Load the trace and save it as a CSV file

if __name__ == "__main__":
    main()
