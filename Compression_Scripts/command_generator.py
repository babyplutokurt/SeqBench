import os
import json

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Analysis_Scripts.size_checker import get_file_size
from path_generator import PathGenerator
from compressor_paths import COMPRESSOR_PATHS
import logging


class CommandGenerator:
    def __init__(self, config_path, path_generator):
        self.config_path = config_path
        self.path_generator = path_generator
        self.config = self.path_generator.load_config()

    def generate_commands(self, job_index, file_pair_index, file_index):
        raise NotImplementedError("Subclasses should implement this method.")


class GzipCommandGenerator(CommandGenerator):
    def generate_commands(self, job_index, file_pair_index, file_index):
        job = self.config['jobs'][job_index]
        normalized_job_name = job['name'].upper()
        if normalized_job_name != "GZIP":
            return []

        executable_path = COMPRESSOR_PATHS.get("GZIP")
        if not executable_path:
            raise ValueError("Path for Spring compressor not found.")

        input_path = self.path_generator.get_input_file_path(job_index, file_pair_index, file_index)
        output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, file_index)
        decompressed_path = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)

        commands = []
        for option in job['options']:
            if "-d" in option:  # Assuming "-d" indicates a decompression option
                command = f"{executable_path} {option} -i {output_path} -o {decompressed_path}"
            else:
                command = f"{executable_path} {option} -d {input_path} -o {output_path}"
            commands.append(command)

        return commands

class BFQZIPCommandGenerator(CommandGenerator):
    def generate_commands(self, job_index, file_pair_index, file_index):
        job = self.config['jobs'][job_index]
        if job['name'].upper() != "BFQZIP":
            return []

        executable_path = COMPRESSOR_PATHS.get("BFQZIP")
        if not executable_path:
            raise ValueError("Path for SZ3 compressor not found.")

        input_path = self.path_generator.get_quality_scores_path(job_index, file_pair_index, file_index)
        output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, file_index)
        decompressed_path = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)

        commands = []

        option = job['options'][0]
        command = f"python3 {executable_path} {input_path} -o {output_path} {option}"
        commands.append(command)

        return commands


class SZ3CommandGenerator(CommandGenerator):
    def generate_commands(self, job_index, file_pair_index, file_index):
        job = self.config['jobs'][job_index]
        if job['name'].upper() != "SZ3":
            return []

        executable_path = COMPRESSOR_PATHS.get("SZ3")
        if not executable_path:
            raise ValueError("Path for SZ3 compressor not found.")

        input_path = self.path_generator.get_quality_scores_path(job_index, file_pair_index, file_index)
        output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, file_index)
        decompressed_path = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)

        if decompressed_path.endswith('.bin.fastq'):
            decompressed_path = decompressed_path[:-6]

        # Replace {Binary_length} in the command options
        compression_options = job['options'][0].replace("{Binary_length}", str("$BINARY_LENGTH"))
        decompression_options = job['options'][1].replace("{Binary_length}", str("$BINARY_LENGTH"))

        compression_command = f"{executable_path} {compression_options} -i {input_path} -z {output_path}"
        decompression_command = f"{executable_path} {decompression_options} -z {output_path} -o {decompressed_path}"

        return [compression_command, decompression_command]


class FQZCompCommandGenerator(CommandGenerator):
    def generate_commands(self, job_index, file_pair_index, file_index):
        job = self.config['jobs'][job_index]
        if job['name'].upper() != "FQZCOMP":
            return []

        executable_path = COMPRESSOR_PATHS.get("FQZCOMP")
        if not executable_path:
            raise ValueError("Path for FQZComp compressor not found.")

        input_path = self.path_generator.get_input_file_path(job_index, file_pair_index, file_index)
        output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, file_index)
        decompressed_path = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)

        commands = []
        for option in job['options']:
            if "-d" in option:  # Assuming "-d" indicates a decompression option
                # Modify the input/output paths for decompression
                decompression_input_path = output_path  # Decompress the previously compressed file
                command = f"{executable_path} {option} {decompression_input_path} {decompressed_path} -X"
            else:
                command = f"{executable_path} {option} {input_path} {output_path}"
            commands.append(command)

        return commands


class SpringCommandGenerator(CommandGenerator):
    def generate_commands(self, job_index, file_pair_index, file_index):
        job = self.config['jobs'][job_index]
        normalized_job_name = job['name'].upper()
        if normalized_job_name != "SPRING":
            return []

        executable_path = COMPRESSOR_PATHS.get("SPRING")
        if not executable_path:
            raise ValueError("Path for Spring compressor not found.")

        input_path = self.path_generator.get_input_file_path(job_index, file_pair_index, file_index)
        output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, file_index)
        decompressed_path = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)

        commands = []
        for option in job['options']:
            if "-d" in option:  # Assuming "-d" indicates a decompression option
                command = f"{executable_path} {option} -i {output_path} -o {decompressed_path}"
            else:
                command = f"{executable_path} {option} -i {input_path} -o {output_path}"
            commands.append(command)

        return commands


class RenanoCommandGenerator(CommandGenerator):
    def generate_commands(self, job_index, file_pair_index, file_index):
        job = self.config['jobs'][job_index]
        if job['name'].upper() != "RENANO":
            return []

        executable_path = COMPRESSOR_PATHS.get("RENANO")
        if not executable_path:
            raise ValueError("Path for Renano compressor not found.")

        input_path = self.path_generator.get_input_file_path(job_index, file_pair_index, file_index)
        output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, file_index)
        decompressed_path = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)

        if job.get('reference_based', False):
            # Reference-based commands
            reference_file = self.path_generator.get_reference_file_path()
            paf_file_path = self.path_generator.get_paf_file_path(job_index, file_pair_index, file_index)
            reference_command = f"minimap2 -x map-ont --secondary=no --cs {reference_file} {input_path} > {paf_file_path}"

            compression_command = f"{executable_path} {job['options'][0]} -r {reference_file} {paf_file_path} {input_path} {output_path}"
            decompression_command = f"{executable_path} -d {job['options'][1]} -r {reference_file} {output_path} {decompressed_path}"

            return [reference_command, compression_command, decompression_command]

        # Non-reference based commands
        compression_command = f"{executable_path} {job['options'][0]} {input_path} {output_path}"
        decompression_command = f"{executable_path} -d {job['options'][1]} {output_path} {decompressed_path}"

        return [compression_command, decompression_command]


class EnanoCommandGenerator(CommandGenerator):
    def generate_commands(self, job_index, file_pair_index, file_index):
        job = self.config['jobs'][job_index]
        if job['name'].upper() != "ENANO":
            return []

        executable_path = COMPRESSOR_PATHS.get("ENANO")
        if not executable_path:
            raise ValueError("Path for Enano compressor not found.")

        input_path = self.path_generator.get_input_file_path(job_index, file_pair_index, file_index)
        output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, file_index)
        decompressed_path = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)

        # Non-reference based commands
        compression_command = f"{executable_path} {job['options'][0]} {input_path} {output_path}"
        decompression_command = f"{executable_path} -d {job['options'][1]} {output_path} {decompressed_path}"

        return [compression_command, decompression_command]


class GenozipCommandGenerator(CommandGenerator):
    def generate_commands(self, job_index, file_pair_index, file_index):
        executable_path = COMPRESSOR_PATHS.get("GENOZIP", ['genozip', 'genounzip'])
        if not executable_path:
            raise ValueError("Path for Genozip compressor not found.")

        job = self.config['jobs'][job_index]
        if job['name'].upper() != "GENOZIP":
            return []

        credential_path = '/home/tus53997/SeqBench2/.genozip_license.v15'
        absolute_credential_path = os.path.abspath(credential_path)
        print("absolute_credential_path: ", absolute_credential_path)

        referenced = self.config['jobs'][job_index].get('reference_based', False)
        paired = self.config['jobs'][job_index].get('pair_compression', False)
        executable_path_compress = executable_path[0]
        executable_path_decompress = executable_path[1]
        if referenced:
            ref_option = f"--reference {self.path_generator.get_reference_file_path()}"
        else:
            ref_option = ''

        if paired:  # paired is not supported right now
            if file_index >= 1:
                return []
            input_path1 = self.path_generator.get_input_file_path(job_index, file_pair_index, 0)
            input_path2 = self.path_generator.get_input_file_path(job_index, file_pair_index, 1)
            output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, 0)
            decompressed_path1 = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, 0)
            decompressed_path2 = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, 1)
            compression_command = f"{executable_path_compress} {ref_option} {job['options'][0]} {input_path1} {input_path2} --pair -o {output_path} --force"
            decompression_command = f"{executable_path_decompress} {ref_option} {job['options'][1]} {output_path} -o {decompressed_path1} {decompressed_path2} --force"
        else:
            input_path = self.path_generator.get_input_file_path(job_index, file_pair_index, file_index)
            output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, file_index)
            decompressed_path = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)
            compression_command = f"{executable_path_compress} {ref_option} {job['options'][0]} {input_path} -o {output_path} --force"
            decompression_command = f"{executable_path_decompress} {ref_option} {job['options'][1]} {output_path} -o {decompressed_path} --force"

        return [compression_command, decompression_command]


class GzipCommandGenerator(CommandGenerator):
    def generate_commands(self, job_index, file_pair_index, file_index):
        executable_path = COMPRESSOR_PATHS.get("GZIP", ['genozip', 'genounzip'])
        if not executable_path:
            raise ValueError("Path for Genozip compressor not found.")

        job = self.config['jobs'][job_index]
        if job['name'].upper() != "GENOZIP":
            return []

        credential_path = './Compressors/External_Dependencies/.genozip_license.v15'
        # absolute_credential_path = os.path.abspath(credential_path)
        print("credential_path: ", credential_path)

        referenced = self.config['jobs'][job_index].get('reference_based', False)
        paired = self.config['jobs'][job_index].get('pair_compression', False)
        print(GenozipCommandGenerator)
        executable_path_compress = executable_path[0]
        executable_path_decompress = executable_path[1]
        if referenced:
            ref_option = f"--reference {self.path_generator.get_reference_file_path()}"
        else:
            ref_option = ''

        if paired:  # paired is not supported right now
            if file_index >= 1:
                return []
            input_path1 = self.path_generator.get_input_file_path(job_index, file_pair_index, 0)
            input_path2 = self.path_generator.get_input_file_path(job_index, file_pair_index, 1)
            output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, 0)
            decompressed_path1 = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, 0)
            decompressed_path2 = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, 1)
            compression_command = f"{executable_path_compress} --licfile {credential_path} {ref_option} {job['options'][0]} {input_path1} {input_path2} --pair -o {output_path} --force"
            decompression_command = f"{executable_path_decompress} --licfile {credential_path} {ref_option} {job['options'][1]} {output_path} -o {decompressed_path1} {decompressed_path2} --force"
        else:
            input_path = self.path_generator.get_input_file_path(job_index, file_pair_index, file_index)
            output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, file_index)
            decompressed_path = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)
            compression_command = f"{executable_path_compress} --licfile {credential_path} {ref_option} {job['options'][0]} {input_path} -o {output_path} --force"
            decompression_command = f"{executable_path_decompress} --licfile {credential_path} {ref_option} {job['options'][1]} {output_path} -o {decompressed_path} --force"

        return [compression_command, decompression_command]


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CommandGeneratorFactory:
    def __init__(self, config_name):
        try:
            self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'jobs', config_name)
            self.config = self.load_config()
            self.path_generator = PathGenerator(self.config_path)
            self.validate_config()
            self.generators = {
                'SZ3': SZ3CommandGenerator(self.config_path, self.path_generator),
                'FQZCOMP': FQZCompCommandGenerator(self.config_path, self.path_generator),
                'SPRING': SpringCommandGenerator(self.config_path, self.path_generator),
                'RENANO': RenanoCommandGenerator(self.config_path, self.path_generator),
                'ENANO': EnanoCommandGenerator(self.config_path, self.path_generator),
                'GENOZIP': GenozipCommandGenerator(self.config_path, self.path_generator),
                'BFQZIP': BFQZIPCommandGenerator(self.config_path, self.path_generator)
            }
        except Exception as e:
            logging.error(f"Failed to initialize command generators: {e}")
            raise

    def load_config(self):
        try:
            with open(self.config_path) as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {self.config_path}")
            raise
        except json.JSONDecodeError:
            logging.error("JSON decoding error occurred while reading the configuration.")
            raise

    def validate_config(self):
        required_fields = ['input_file', 'jobs']
        for field in required_fields:
            if field not in self.config:
                logging.error(f"Configuration missing required field: {field}")
                raise ValueError(f"Configuration missing required field: {field}")

    def generate_all_commands(self):
        all_commands_for_files = []
        for file_pair_index, file_pair in enumerate(self.config['input_file']):
            commands_for_current_file_pair = []
            for job_index, job in enumerate(self.config['jobs']):
                command_for_current_job = []
                generator = self.generators.get(job['name'].upper())
                if generator:
                    for file_index in range(len(file_pair)):
                        try:
                            job_commands = generator.generate_commands(job_index, file_pair_index, file_index)
                            command_for_current_job.append(job_commands)
                        except Exception as e:
                            logging.warning(
                                f"Failed to generate commands for job {job['name']} at index {job_index}: {e}")
                else:
                    logging.info(f"No generator found for {job['name']}. Skipping...")
                commands_for_current_file_pair.append(command_for_current_job)
            all_commands_for_files.append(commands_for_current_file_pair)
        return all_commands_for_files


if __name__ == "__main__":
    config_path = "../Jobs/genozip.json"
    factory = CommandGeneratorFactory(config_path)
    all_commands = factory.generate_all_commands()
    for file_pair_index, file_commands in enumerate(all_commands):
        for job_index, command_set in enumerate(file_commands):
            for file_index, command in enumerate(command_set):
                print(f"File Pair: {file_pair_index}, File: {file_index}, Job: {job_index}")
                for cmd in command:
                    print(cmd)
                print('-' * 50)
