import os
import csv
import sys
import subprocess
import logging
from jinja2 import Template
from command_generator import CommandGeneratorFactory
from dependency_linker import DependencyLinker

sys.path.append('../')
sys.path.append(os.path.join(os.path.dirname(__file__), 'build'))
import fastq_processor


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


class JobGenerator:
    def __init__(self, config_name,
                 template_path,
                 fast_split_template,
                 fast_reconstruct_template):
        self.factory = CommandGeneratorFactory(config_name)
        self.config = self.factory.config
        self.path_generator = self.factory.path_generator
        self.template_path = template_path
        self.dependency_linker = DependencyLinker()
        self.all_commands = self.factory.generate_all_commands()
        self.fast_split_template = fast_split_template
        self.fast_reconstruct_template = fast_reconstruct_template

    def create_compression_metrics_csv(self, file_pair_index, file_index):
        metrics_path = self.path_generator.get_compression_metric_path(file_pair_index, file_index)
        header = ['job_id_compression', 'Compressor_Name', 'Compression_Time', 'Compression_Throughput',
                  'Decompression_Time', 'Decompression_Throughput', 'Ratio']
        os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
        with open(metrics_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
        logging.info(f"Created CSV file for compression metrics: {metrics_path}")

    def create_job_script(self, job_name, commands, job_index, file_pair_index, file_index,
                          dependencies=None):
        if not dependencies:
            dependencies = []
        job_script_path = self.path_generator.get_script_path(job_index, file_pair_index, file_index)

        with open(self.template_path) as f:
            template = Template(f.read())

        reference_command = ''
        if len(commands) == 1:
            compression_command = commands[0]
            decompression_command = ""
        elif len(commands) >= 3:
            reference_command = commands[0]
            compression_command = commands[1]
            decompression_command = commands[2]
        else:
            compression_command = commands[0]
            decompression_command = commands[1]
        referenced = self.config['jobs'][job_index].get("reference_based", False)
        input_path = self.path_generator.get_input_file_path(job_index, file_pair_index, file_index)
        binary_input_file = self.path_generator.get_quality_scores_path(job_index, file_pair_index, file_index)
        compressed_output_path = self.path_generator.get_compressed_output_path(job_index, file_pair_index, file_index)
        metrics_csv_path = self.path_generator.get_compression_metric_path(file_pair_index, file_index)
        output_log = self.path_generator.get_output_log_path(job_index, file_pair_index, file_index)
        error_log = self.path_generator.get_error_log_path(job_index, file_pair_index, file_index)
        compressor_name = self.path_generator.get_compressor_name(job_index, file_pair_index, file_index)
        if referenced:
            compressor_name += '_referenced'
        nodes = self.config.get('nodes', 1)  # Default to 1 node if not specified
        ppn = self.config.get('ppn', 8)  # Default to 8 processor per node if not specified
        conda_path = self.config.get('conda_path', '/home/tus53997/miniconda3/bin/activate')
        walltime = self.config.get('walltime', "24:00:00")
        email = self.config.get('email', "default@gamil.com")
        node_size = 'normal'
        compressor = self.config['jobs'][job_index]['name'].upper()
        active_dependencies = []
        for dep in dependencies:
            job_status = check_job_status_depend(dep)
            if job_status:
                active_dependencies.append(dep)

        dependency_line = f"#PBS -W depend=afterok:{':'.join(active_dependencies)}\n" if active_dependencies else ""
        job_name = f"compression_{file_pair_index}_{job_index}_{file_index}"

        job_script_content = template.render(
            compressor=compressor,
            job_name=job_name,
            nodes=nodes,
            ppn=ppn,
            node_size=node_size,
            walltime=walltime,
            conda_path=conda_path,
            email=email,
            output_log=output_log,
            error_log=error_log,
            reference_command=reference_command,
            compression_command=compression_command,
            decompression_command=decompression_command,
            input_path=input_path,
            binary_input_file=binary_input_file,
            compressed_output_path=compressed_output_path,
            metrics_csv_path=metrics_csv_path,
            compressor_name=compressor_name,
            dependency_line=dependency_line
        )

        with open(job_script_path, 'w') as f:
            f.write(job_script_content)

        logging.info(f"Created job script: {job_script_path}")
        return job_script_path

    def submit_job(self, job_script_path, job_name, use_append=False):
        submit_command = f"qsub {job_script_path}"  # Change this if using a different scheduler like `sbatch` for SLURM
        try:
            result = subprocess.run(submit_command, check=True, shell=True, capture_output=True, text=True)
            job_id = result.stdout.strip().split('.')[0]  # Get the job ID from the output
            if use_append:
                self.dependency_linker.append_job_id(job_name, job_id)
            else:
                self.dependency_linker.add_job_id(job_name, job_id)
            logging.info(f"Job submitted: {job_script_path} with job ID: {job_id}")
            return job_id
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to submit job: {job_script_path}, Error: {e}")
            return None

    def generate_and_submit_pre_processing_jobs(self):
        preprocessing_job_ids = []
        for file_pair_index, file_pair in enumerate(self.config['input_file']):
            for file_index in range(len(file_pair)):
                job_name = f"pre_processing_{file_pair_index}_{file_index}"
                input_path = self.path_generator.get_input_file_path(0, file_pair_index, file_index)
                output_bases_id_path = self.path_generator.get_bases_id_path(0, file_pair_index, file_index)
                output_bases_path = self.path_generator.get_dna_bases_path(0, file_pair_index, file_index)
                output_quality_id_path = self.path_generator.get_quality_id_path(0, file_pair_index, file_index)
                output_quality_path = self.path_generator.get_quality_scores_path(0, file_pair_index, file_index)
                output_log = self.path_generator.get_output_log_path(0, file_pair_index, file_index, 'fastq_split')
                error_log = self.path_generator.get_error_log_path(0, file_pair_index, file_index, 'fastq_split')
                nodes = self.config.get('nodes', 1)  # Default to 1 node if not specified
                ppn = self.config.get('ppn', 8)  # Default to 8 processor per node if not specified
                conda_path = self.config.get('conda_path', '/home/tus53997/miniconda3/bin/activate')
                walltime = self.config.get('walltime', "24:00:00")
                email = self.config.get('email', "default@gamil.com")
                build_pre_processing_cpp_path = self.path_generator.get_build_pre_processing_cpp_path()

                with open(self.fast_split_template) as f:
                    template = Template(f.read())

                job_script_content = template.render(
                    job_name=job_name,
                    nodes=nodes,
                    ppn=ppn,
                    walltime=walltime,
                    input_path=input_path,
                    output_bases_id_path=output_bases_id_path,
                    output_bases_path=output_bases_path,
                    output_quality_id_path=output_quality_id_path,
                    output_quality_path=output_quality_path,
                    get_build_pre_processing_cpp_path=build_pre_processing_cpp_path,
                    output_log=output_log,
                    error_log=error_log,
                    conda_path=conda_path,
                    email=email
                )

                script_path = self.path_generator.get_pre_processing_script_path(0, file_pair_index, file_index)
                with open(script_path, 'w') as script_file:
                    script_file.write(job_script_content)

                logging.info(f"Created preprocessing job script: {script_path}")
                job_id = self.submit_job(script_path, job_name)
                if job_id:
                    preprocessing_job_ids.append(job_id)
                    for job_index, job in enumerate(self.config['jobs']):
                        if job['name'].upper() == "SZ3":
                            dependent_job_name = f"job_{file_pair_index}_{job_index}_{file_index}"
                            self.dependency_linker.add_job_id(dependent_job_name, job_id)
        return preprocessing_job_ids

    def generate_and_submit_reconstruct_jobs(self, job_name, job_index, file_pair_index, file_index, dependencies,
                                             ):
        build_fastq_reconstruct_cpp_path = self.path_generator.get_build_fastq_reconstruct_cpp_path()
        job_name = f"fastq_reconstruct_{file_pair_index}_{file_index}"
        output_bases_id_path = self.path_generator.get_bases_id_path(job_index, file_pair_index, file_index)
        output_bases_path = self.path_generator.get_dna_bases_path(job_index, file_pair_index, file_index)
        output_quality_id_path = self.path_generator.get_quality_id_path(job_index, file_pair_index, file_index)
        output_quality_path = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)
        if output_quality_path.endswith('.bin.fastq'):
            output_quality_path = output_quality_path[:-6]

        output_path = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, file_index)
        # output_path = output_path.replace('{Binary_length}', str(bianry_length))
        output_log = self.path_generator.get_output_log_path(0, file_pair_index, file_index, 'fastq_reconstruct')
        error_log = self.path_generator.get_error_log_path(0, file_pair_index, file_index, 'fastq_reconstruct')
        nodes = self.config.get('nodes', 1)  # Default to 1 node if not specified
        ppn = self.config.get('ppn', 8)  # Default to 8 processor per node if not specified
        conda_path = self.config.get('conda_path', '/home/tus53997/miniconda3/bin/activate')
        walltime = self.config.get('walltime', "24:00:00")
        email = self.config.get('email', "default@gamil.com")

        active_dependencies = []
        for dep in dependencies:
            job_status = check_job_status_depend(dep)
            if job_status:
                active_dependencies.append(dep)

        dependency_line = f"#PBS -W depend=afterok:{':'.join(active_dependencies)}\n" if active_dependencies else ""

        with open(self.fast_reconstruct_template) as f:
            template = Template(f.read())

        job_script_content = template.render(
            job_name=job_name,
            nodes=nodes,
            ppn=ppn,
            walltime=walltime,
            output_bases_id_path=output_bases_id_path,
            output_bases_path=output_bases_path,
            output_quality_id_path=output_quality_id_path,
            output_quality_path=output_quality_path,
            output_path=output_path,
            get_build_pre_processing_cpp_path=build_fastq_reconstruct_cpp_path,
            output_log=output_log,
            error_log=error_log,
            conda_path=conda_path,
            dependency_line=dependency_line,
            email=email
        )

        script_path = self.path_generator.get_fastq_reconstruct_script_path(job_index, file_pair_index, file_index)
        with open(script_path, 'w') as script_file:
            script_file.write(job_script_content)

        logging.info(f"Created reconstruction job script: {script_path}")
        job_id = self.submit_job(script_path, job_name)
        dependent_job_name = f"job_{file_pair_index}_{job_index}_{file_index}"
        self.dependency_linker.add_job_id(dependent_job_name, job_id)
        return job_id

    def generate_and_submit_jobs(self):
        # Step 1: Create CSV files for each input file
        for file_pair_index, file_pair in enumerate(self.config['input_file']):
            for file_index in range(len(file_pair)):
                self.create_compression_metrics_csv(file_pair_index, file_index)

        # Step 2: FastQ split for SZ3
        preprocessing_jobs = []
        for job_index, job in enumerate(self.config['jobs']):
            if job['name'].upper() == "SZ3":
                preprocessing_job_ids = self.generate_and_submit_pre_processing_jobs()
                break

        # Step 3: Create and submit job scripts with dependencies
        previous_job_ids = []
        for file_pair_index, file_pair in enumerate(self.config['input_file']):
            for job_index in range(len(self.config['jobs'])):
                for file_index in range(len(file_pair)):
                    job_name = f"job_{file_pair_index}_{job_index}_{file_index}"
                    if self.config['jobs'][job_index]['name'].upper() == 'SZ3':
                        previous_job_ids = self.dependency_linker.get_dependencies(job_name)

                    job_script_path = self.create_job_script(
                        job_name,
                        self.all_commands[file_pair_index][job_index][file_index],
                        job_index,
                        file_pair_index,
                        file_index,
                        dependencies=previous_job_ids
                    )
                    job_id = self.submit_job(job_script_path, job_name)
                    if job_id:
                        self.dependency_linker.add_job_id(job_name, job_id)
                        previous_job_ids = []

        # Step 4: FastQ reconstruct for SZ3
        for file_pair_index, file_pair in enumerate(self.config['input_file']):
            for job_index in range(len(self.config['jobs'])):
                for file_index in range(len(file_pair)):
                    if self.config['jobs'][job_index]['name'].upper() == 'SZ3':
                        job_name = f"job_{file_pair_index}_{job_index}_{file_index}"
                        dependencies = self.dependency_linker.get_dependencies(job_name)
                        self.generate_and_submit_reconstruct_jobs(job_name, job_index, file_pair_index, file_index,
                                                                  dependencies)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname=s - %(message=s')
    config_name = "../Jobs/bench2.json"
    job_generator = JobGenerator(config_name)
    job_generator.generate_and_submit_jobs()
