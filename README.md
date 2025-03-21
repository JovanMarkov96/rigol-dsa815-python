# Rigol DSA815 Python

This project provides a Python interface for interacting with the Rigol DSA815 spectrum analyzer. It includes functionality for initializing the device, performing measurements, and processing the resulting data.

## Overview

The Rigol DSA815 is a versatile spectrum analyzer that can be controlled programmatically using this Python library. This project aims to simplify the process of automating measurements and data collection from the device.

## Features

- Initialize the Rigol DSA815 device
- Perform various types of measurements
- Process and analyze measurement data
- Save and load measurement configurations
- Generate reports from measurement data

## Installation

To get started with the Rigol DSA815 Python library, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rigol-dsa815-python.git
   ```

2. Navigate to the project directory:
   ```
   cd rigol-dsa815-python
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To use the library, you can run the main application:

```
python src/main.py
```

### Example

Here is a simple example of how to use the library to initialize the device and perform a measurement using the `DSA815.py` file:

```python
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
```

To run the example, execute the following command:

```
python src/DSA815.py
```

For more detailed usage, refer to the documentation in the `docs` directory.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
