def count_base_lines(fastq_file):
    """
    Counts the number of lines that contain base sequences in a FASTQ file.

    Args:
        fastq_file (str): Path to the FASTQ file.

    Returns:
        int: Number of base sequence lines in the FASTQ file.
    """
    try:
        with open(fastq_file, 'r') as file:
            # Initialize the counter for base lines
            base_line_count = 0
            # Iterate over the file lines
            for i, line in enumerate(file):
                # Every 4th line starting from the second line contains base sequences
                if i % 4 == 1:
                    base_line_count += 1
        return base_line_count
    except FileNotFoundError:
        print(f"File not found: {fastq_file}")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0


# Example usage
fastq_file_path = ""
base_lines = count_base_lines(fastq_file_path)
print(f"Number of base sequence lines in the FASTQ file: {base_lines}")
