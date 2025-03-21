# Rigol DSA815 Python

This project provides a Python interface for interacting with the Rigol DSA815 spectrum analyzer. It includes functionality for initializing the device, performing measurements, and processing the resulting data.

## Overview

The Rigol DSA815 is a versatile spectrum analyzer that can be controlled programmatically using this Python library. This project aims to simplify the process of automating measurements and data collection from the device.

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

Here is a simple example of how to use the library to initialize the device and perform a measurement:

```python
from src.main import initialize_device, perform_measurement

device = initialize_device()
result = perform_measurement(device)
print(result)
```

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.