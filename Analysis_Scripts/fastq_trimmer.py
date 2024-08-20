import argparse


def extract_lines(num, input_file, output_file):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for _ in range(num * 4):
                line = infile.readline()
                if not line:
                    break
                outfile.write(line)
        print(f"Successfully created {output_file} with the first {num} records from {input_file}.")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(description='Extract the first num lines from a FASTQ file.')
    parser.add_argument('num', type=int, help='Number of lines to extract')
    parser.add_argument('input_file', type=str, help='Input FASTQ file')
    parser.add_argument('output_file', type=str, help='Output FASTQ file')

    args = parser.parse_args()

    extract_lines(args.num, args.input_file, args.output_file)


if __name__ == "__main__":
    extract_lines("")


