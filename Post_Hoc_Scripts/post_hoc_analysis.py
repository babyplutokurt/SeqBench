import csv
import json
import os
import subprocess
import logging
from jinja2 import Template
import sys

sys.path.append('../')
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


class PostHocAnalysis:
    def __init__(self, config_name,
                 template_path,
                 job_template_path):
        self.config = self.load_config(config_name)
        self.path_generator = PathGenerator(config_name)
        self.dependency_linker = DependencyLinker()
        self.template_path = template_path
        self.job_template_path = job_template_path

    def load_config(self, config_path):
        try:
            with open(config_path) as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            raise Exception(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError:
            raise Exception(f"Error decoding JSON from the configuration file: {config_path}")

    def create_post_hoc_metrics_csv(self, file_pair_index, file_index):
        metrics_path = self.path_generator.get_post_hoc_metric_path(file_pair_index, file_index)
        header = ['job_id', 'Compressor_Name', 'True_Positives(TP)', 'False_Positives(FP)', 'False_Negatives(FN)',
                  'Precision', 'Recall', 'F1_Score']
        # Ensure the directory exists
        os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
        with open(metrics_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
        logging.info(f"Created CSV file for Post-hoc metrics: {metrics_path}")


    def create_original_files_vcf_script(self, job_name="truth_vcf", file_pair_index=0,
                                         file_index=0, dependencies=[], job_index = 0):
        input_fastq_1 = self.path_generator.get_input_file_path(job_index, file_pair_index, 0)
        if len(self.config['input_file'][file_pair_index]) > 1:
            input_fastq_2 = self.path_generator.get_input_file_path(job_index, file_pair_index, 1)
        else:
            input_fastq_2 = ''
        reference_file = self.path_generator.get_reference_file_path()
        sam_path = self.path_generator.get_truth_sam_path(job_index, file_pair_index, file_index)
        sorted_bam_path = self.path_generator.get_truth_sorted_bam_path(job_index, file_pair_index, file_index)
        variant_path = self.path_generator.get_truth_variant_path(job_index, file_pair_index, file_index)
        compressed_variant_path = self.path_generator.get_truth_compressed_variant_path(job_index, file_pair_index,
                                                                                        file_index)
        job_name = f'truth_vcf_{file_pair_index}'
        output_log = self.path_generator.get_post_hoc_truth_output_log_path(job_index, file_pair_index, file_index)
        error_log = self.path_generator.get_post_hoc_truth_error_log_path(job_index, file_pair_index, file_index)
        nodes = self.config.get('nodes', 1)  # Default to 1 node if not specified
        ppn = self.config.get('ppn', 8)  # Default to 8 processor per node if not specified
        conda_path = self.config.get('conda_path', '/home/tus53997/miniconda3/bin/activate')
        walltime = self.config.get('walltime', "24:00:00")
        email = self.config.get('email', "default@gamil.com")

        with open(self.template_path) as f:
            template = Template(f.read())

        dependency_line = f"#PBS -W depend=afterok:{':'.join(dependencies)}\n" if dependencies else ""

        job_script_content = template.render(
            job_name=job_name,
            nodes=nodes,
            ppn=ppn,
            walltime=walltime,
            conda_path=conda_path,
            email=email,
            output_log=output_log,
            error_log=error_log,
            threads=nodes * ppn,
            reference_file=reference_file,
            input_fastq_1=input_fastq_1,
            input_fastq_2=input_fastq_2,
            sam_path=sam_path,
            sorted_bam_path=sorted_bam_path,
            variant_path=variant_path,
            compressed_variant_path=compressed_variant_path,
            dependency_line=dependency_line
        )

        job_script_path = self.path_generator.get_truth_vcf_script_path(job_index, file_pair_index, file_index)
        with open(job_script_path, 'w') as f:
            f.write(job_script_content)

        logging.info(f"Created job script: {job_script_path}")
        return job_script_path

    def create_decompressed_files_vcf_script(self, job_name="lossy_vcf", job_index=0,
                                             file_pair_index=0,
                                             file_index=0, dependencies=None):
        input_fastq_1 = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, 0)
        if len(self.config["input_file"][file_pair_index]) > 1:
            input_fastq_2 = self.path_generator.get_decompressed_output_path(job_index, file_pair_index, 1)
        else:
            input_fastq_2 = ''
        reference_file = self.path_generator.get_reference_file_path()
        sam_path = self.path_generator.get_sam_path(job_index, file_pair_index, file_index)
        sorted_bam_path = self.path_generator.get_sorted_bam_path(job_index, file_pair_index, file_index)
        variant_path = self.path_generator.get_variant_path(job_index, file_pair_index, file_index)
        compressed_variant_path = self.path_generator.get_compressed_variant_path(job_index, file_pair_index,
                                                                                  file_index)
        original_vcf = self.path_generator.get_truth_compressed_variant_path(0, file_pair_index,
                                                                             0)  # Assuming the first job is for the original VCF
        comparison_dir = self.path_generator.get_comparison_dir_path(job_index, file_pair_index, file_index)
        compressor_name = self.path_generator.get_compressor_name(job_index, file_pair_index, file_index)
        metrics_csv_path = self.path_generator.get_post_hoc_metric_path(file_pair_index, file_index)

        output_log = self.path_generator.get_post_hoc_output_log_path(job_index, file_pair_index, file_index)
        error_log = self.path_generator.get_post_hoc_error_log_path(job_index, file_pair_index, file_index)
        nodes = self.config.get('nodes', 1)  # Default to 1 node if not specified
        ppn = self.config.get('ppn', 8)  # Default to 8 processor per node if not specified
        conda_path = self.config.get('conda_path', '/home/tus53997/miniconda3/bin/activate')
        walltime = self.config.get('walltime', "24:00:00")
        email = self.config.get('email', "default@gamil.com")

        with open(self.job_template_path) as f:
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
            output_log=output_log,
            error_log=error_log,
            threads=nodes * ppn,
            reference_file=reference_file,
            input_fastq_1=input_fastq_1,
            input_fastq_2=input_fastq_2,
            sam_path=sam_path,
            sorted_bam_path=sorted_bam_path,
            variant_path=variant_path,
            compressed_variant_path=compressed_variant_path,
            original_vcf=original_vcf,
            comparison_dir=comparison_dir,
            metrics_csv_path=metrics_csv_path,
            compressor_name=compressor_name,
            dependency_line=dependency_line
        )

        job_script_path = self.path_generator.get_lossy_vcf_script_path(job_index, file_pair_index, file_index)
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

    def run_posthoc_analysis(self, job_name="truth_vcf", dependencies=None):

        # Step 1: Create CSV files for each input pair
        for file_pair_index, file_pair in enumerate(self.config['input_file']):
            self.create_post_hoc_metrics_csv(file_pair_index, 0)
        for file_pair_index, file_pair in enumerate(self.config['input_file']):

                script_path = self.create_original_files_vcf_script(job_name, file_pair_index,
                                                                    file_index=0)
                job_id = self.submit_job(script_path)
                if job_id:
                    for job_index in range(len(self.config['jobs'])):
                        for file_index in range(len(file_pair)):
                            job_name = f"job_{file_pair_index}_{job_index}_{file_index}"
                            self.dependency_linker.append_job_id(job_name, job_id)

        for file_pair_index, file_pair in enumerate(self.config['input_file']):
            for job_index in range(len(self.config['jobs'])):
                job_name = f"post_hoc_{file_pair_index}_{job_index}_{0}"
                prev_job_name_2 = f"job_{file_pair_index}_{job_index}_{1}"
                prev_job_name = f"job_{file_pair_index}_{job_index}_{0}"
                dependencies = list(
                    set(self.dependency_linker.get_dependencies(
                        prev_job_name) + self.dependency_linker.get_dependencies(
                        prev_job_name_2)))
                lossy_script_path = self.create_decompressed_files_vcf_script(job_name, job_index,
                                                                              file_pair_index, 0,
                                                                              dependencies)
                self.submit_job(lossy_script_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config_name = "/home/tus53997/SeqBench2/Jobs/bench.json"
    truth_vcf_template = '/home/tus53997/SeqBench2/Scripts_Template/Compute_Node/Compute_truth_vcf.sh'
    post_hoc_template = '/home/tus53997/SeqBench2/Scripts_Template/Compute_Node/Compute_post_hoc.sh'
    post_hoc_analysis = PostHocAnalysis(config_name, truth_vcf_template, post_hoc_template)
    job_name = "truth_vcf"
    # print(post_hoc_analysis.check_job_status(71595))
    post_hoc_analysis.run_posthoc_analysis()
