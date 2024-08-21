import csv
import json
import os
import subprocess
import logging
from jinja2 import Template
import sys

sys.path.append('../')
sys.path.append(os.path.join(os.path.dirname(__file__), 'build'))
import fastq_metrics
from Compression_Scripts.path_generator import PathGenerator
from Compression_Scripts.dependency_linker import DependencyLinker


def check_job_status_depend(job_id):
    check_command = f"qstat -f {job_id}"
    try:
        result = subprocess.run(check_command, check=True, shell=True, capture_output=True, text=True)
        output = result.stdout
        if "job_state = R" in output:
            return True  # Running or other states
        elif "job_state = H" in output:
            return True
        elif "job_state = Q" in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        return False


class ErrorAnalysis:
    def __init__(self, config_name, template_path):
        self.config = self.load_config(config_name)
        self.path_generator = PathGenerator(config_name)
        self.dependency_linker = DependencyLinker()
        self.template_path = template_path

    def load_config(self, config_path):
        try:
            with open(config_path) as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            raise Exception(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError:
            raise Exception(f"Error decoding JSON from the configuration file: {config_path}")

    def create_error_analysis_metrics_csv(self, file_pair_index, file_index):
        metrics_path = self.path_generator.get_error_analysis_metric_path(file_pair_index, file_index)
        header = ['job_id', 'Compressor_Name', 'MSE_v3', 'PSNR_v3']
        # Ensure the directory exists
        os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
        with open(metrics_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
        logging.info(f"Created CSV file for Error Analysis metrics: {metrics_path}")

    def create_error_analysis_script(self, job_name, job_index, file_pair_index, file_index,
                                     dependencies=[]):
        original_file = self.path_generator.get_input_file_path(0, file_pair_index, file_index)
        decompressed_file = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)
        metrics_csv_path = self.path_generator.get_error_analysis_metric_path(file_pair_index, file_index)
        compressor_name = self.path_generator.get_compressor_name(job_index, file_pair_index, file_index)
        build_cpp_path = self.path_generator.get_build_cpp_path()
        output_log = self.path_generator.get_error_analysis_output_log_path(job_index, file_pair_index, file_index)
        error_log = self.path_generator.get_error_analysis_error_log_path(job_index, file_pair_index, file_index)

        nodes = self.config.get('nodes', 1)  # Default to 1 node if not specified
        ppn = self.config.get('ppn', 8)  # Default to 8 processor per node if not specified
        conda_path = self.config.get('conda_path', '')
        walltime = self.config.get('walltime', "24:00:00")
        email = self.config.get('email', "default@gamil.com")
        node_size = self.config.get('node_size', 'normal')

        with open(self.template_path) as f:
            template = Template(f.read())

        active_dependencies = []
        for dep in dependencies:
            job_status = check_job_status_depend(dep)
            if job_status:
                active_dependencies.append(dep)
        dependency_line = f"#PBS -W depend=afterok:{':'.join(active_dependencies)}\n" if active_dependencies else ""

        job_script_content = template.render(
            job_name=job_name,
            nodes=nodes,
            ppn=ppn,
            walltime=walltime,
            conda_path=conda_path,
            email=email,
            node_size=node_size,
            original_file=original_file,
            decompressed_file=decompressed_file,
            metrics_csv_path=metrics_csv_path,
            compressor_name=compressor_name,
            output_log=output_log,
            error_log=error_log,
            threads=nodes * ppn,
            build_cpp_path=build_cpp_path,
            dependency_line=dependency_line
        )

        job_script_path = self.path_generator.get_error_analysis_script_path(job_index, file_pair_index, file_index)
        with open(job_script_path, 'w') as f:
            f.write(job_script_content)

        logging.info(f"Created job script: {job_script_path}")
        return job_script_path

    def submit_job(self, job_script_path):
        submit_command = f"qsub {job_script_path}"
        try:
            result = subprocess.run(submit_command, check=True, shell=True, capture_output=True, text=True)
            job_id = result.stdout.strip().split('.')[0]  # Get the job ID from the output
            logging.info(f"Job submitted: {job_script_path} with job ID: {job_id}")
            return job_id
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to submit job: {job_script_path}, Error: {e}")
            return None

    def run_error_analysis(self):
        # Step 1: Create CSV files for each input file
        for file_pair_index, file_pair in enumerate(self.config['input_file']):
            for file_index in range(len(file_pair)):
                self.create_error_analysis_metrics_csv(file_pair_index, file_index)

        # Step 2: Generate and submit job scripts for error analysis
        for file_pair_index, file_pair in enumerate(self.config['input_file']):
            for job_index in range(len(self.config['jobs'])):
                for file_index in range(len(file_pair)):
                    job_name = f"error_analysis_{file_pair_index}_{job_index}_{file_index}"
                    prev_job_name = f"job_{file_pair_index}_{job_index}_{file_index}"
                    dependencies = self.dependency_linker.get_dependencies(prev_job_name)
                    script_path = self.create_error_analysis_script(job_name, job_index,
                                                                    file_pair_index, file_index, dependencies)
                    self.submit_job(script_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config_name = "../Jobs/bench.json"
    error_analysis = ErrorAnalysis(config_name)
    error_analysis.run_error_analysis()
