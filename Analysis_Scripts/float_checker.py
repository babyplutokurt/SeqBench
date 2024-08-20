import struct
import os


def detect_data_type(file_path):
    # Read a chunk of the binary file
    with open(file_path, 'rb') as f:
        data = f.read(1024)  # Read the first 1024 bytes

    # Check the size of the data
    if len(data) < 4:
        print("File is too small to determine the data type.")
        return

    # Try interpreting the data as floats and integers
    float_values = []
    int_values = []

    for i in range(0, len(data) - 4, 4):
        chunk = data[i:i + 4]
        float_value = struct.unpack('f', chunk)[0]
        int_value = struct.unpack('i', chunk)[0]
        float_values.append(float_value)
        int_values.append(int_value)

    # Check the variance in the values
    float_variance = max(float_values) - min(float_values)
    int_variance = max(int_values) - min(int_values)

    print("Float values sample:", float_values[:10])
    print("Integer values sample:", int_values[:10])



# Example usage
file_path = '/scratch/tus53997/FASTQ/FASTQ_fields/ERR1044277_1_1000000_quality_scores.bin'
detect_data_type(file_path)
