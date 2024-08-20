import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Analysis_Scripts.size_checker import get_file_size  # Ensure this path is correct based on your project structure


class PathGenerator:
    def __init__(self, config_path):
        self.config_path = config_path
        self.project_base_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        self.config = self.load_config()
        self.storage_dir = self.config.get('storage_dir', self.project_base_dir)
        if self.storage_dir == '':
            self.storage_dir = self.project_base_dir

    def load_config(self):
        try:
            with open(self.config_path) as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            raise Exception(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError:
            raise Exception(f"Error decoding JSON from the configuration file: {self.config_path}")

    def get_full_path(self, relative_path):
        if os.path.isabs(relative_path):
            return os.path.normpath(relative_path)
        full_path = os.path.abspath(os.path.join(self.project_base_dir, relative_path))
        return full_path

    def ensure_directory_exists(self, path):
        os.makedirs(path, exist_ok=True)

    def get_reference_file_path(self):
        reference_file = self.config['reference_file']
        return self.get_full_path(reference_file)

    def get_input_file_path(self, job_index, file_pair_index, file_index):
        file_set = 'input_file'
        input_files = self.config[file_set][file_pair_index]
        return self.get_full_path(input_files[file_index])

    def replace_extension(self, file_name, new_extension):
        base_name, file_ext = os.path.splitext(file_name)
        if file_ext in ['.fastq', '.fq', '.fnq']:
            return base_name + new_extension
        else:
            raise ValueError(f"Unexpected file extension: {file_ext}")

    def get_bases_id_path(self, job_index, file_pair_index, file_index):
        input_file_path = self.get_input_file_path(job_index, file_pair_index, file_index)
        base_dir = os.path.join(os.path.dirname(input_file_path), "FASTQ_fields")
        self.ensure_directory_exists(base_dir)
        base_file_name = os.path.basename(input_file_path)
        base_name = self.replace_extension(base_file_name, '_base_id.fastq')
        return os.path.join(base_dir, base_name)

    def get_dna_bases_path(self, job_index, file_pair_index, file_index):
        input_file_path = self.get_input_file_path(job_index, file_pair_index, file_index)
        base_dir = os.path.join(os.path.dirname(input_file_path), "FASTQ_fields")
        self.ensure_directory_exists(base_dir)
        base_file_name = os.path.basename(input_file_path)
        base_name = self.replace_extension(base_file_name, '_dna_bases.fastq')
        return os.path.join(base_dir, base_name)

    def get_quality_id_path(self, job_index, file_pair_index, file_index):
        input_file_path = self.get_input_file_path(job_index, file_pair_index, file_index)
        base_dir = os.path.join(os.path.dirname(input_file_path), "FASTQ_fields")
        self.ensure_directory_exists(base_dir)
        base_file_name = os.path.basename(input_file_path)
        base_name = self.replace_extension(base_file_name, '_quality_id.fastq')
        return os.path.join(base_dir, base_name)

    def get_quality_scores_path(self, job_index, file_pair_index, file_index):
        job_name = self.config['jobs'][job_index]['name'].upper()

        if job_name != 'SZ3':
            return self.get_input_file_path(job_index, file_pair_index, file_index)

        input_file_path = self.get_input_file_path(job_index, file_pair_index, file_index)
        base_dir = os.path.join(os.path.dirname(input_file_path), "FASTQ_fields")
        self.ensure_directory_exists(base_dir)

        base_file_name = os.path.basename(input_file_path)
        base_name = self.replace_extension(base_file_name, '_quality_scores.bin')
        return os.path.join(base_dir, base_name)

    def get_paf_file_path(self, job_index, file_pair_index, file_index):
        input_file_path = self.get_input_file_path(job_index, file_pair_index, file_index)
        input_file_name = self.replace_extension(os.path.basename(input_file_path), '.paf')
        paf_file_path = os.path.abspath(os.path.join(self.storage_dir, 'RefSeq', input_file_name))
        self.ensure_directory_exists(os.path.dirname(paf_file_path))
        return paf_file_path

    def get_compressed_output_path(self, job_index, file_pair_index, file_index):
        input_file_path = self.get_input_file_path(job_index, file_pair_index, file_index)
        job_name = self.config['jobs'][job_index]['name'].upper()
        option_str = self.config['jobs'][job_index]['options'][0]  # Get the first option
        sanitized_option_str = option_str.replace(" ", "_").replace("/", "_")
        referenced = self.config['jobs'][job_index].get('reference_based', False)
        if referenced:
            sanitized_option_str += '_referenced'
        suffix_mapper = {
            "SZ3": ".sz",
            "FQZCOMP": ".fqz",
            "SPRING": ".spring",
            "RENANO": ".renano",
            "ENANO": ".enano",
            "GENOZIP": ".genozip",
            "BFQZIP": ".fq"
        }
        suffix = suffix_mapper.get(job_name, ".out")
        base_filename = os.path.basename(input_file_path)
        compressed_output_dir = os.path.abspath(os.path.join(self.storage_dir, 'CompressedOutput'))
        self.ensure_directory_exists(compressed_output_dir)

        if job_name == 'BFQZIP':
            decompressed_output_dir = os.path.abspath(os.path.join(self.storage_dir, 'DecompressedOutput'))
            compressed_file_name = f"{base_filename}_{sanitized_option_str}"
            return os.path.join(decompressed_output_dir, compressed_file_name)
        compressed_file_name = f"{base_filename}_{sanitized_option_str}{suffix}"
        return os.path.join(compressed_output_dir, compressed_file_name)

    def get_decompressed_output_path(self, job_index, file_pair_index, file_index):
        compressed_path = self.get_compressed_output_path(job_index, file_pair_index, file_index)
        decompressed_output_dir = os.path.abspath(os.path.join(self.storage_dir, 'DecompressedOutput'))
        self.ensure_directory_exists(decompressed_output_dir)
        if self.config['jobs'][job_index]['name'].upper() == 'BFQZIP':
            decompressed_file_name = f"{os.path.basename(compressed_path)}.fq"
        elif self.config['jobs'][job_index]['name'].upper() == 'SZ3':
            decompressed_file_name = f"{os.path.basename(compressed_path)}.bin.fastq"
        else:
            decompressed_file_name = f"{os.path.basename(compressed_path)}.fastq"
        return os.path.join(decompressed_output_dir, decompressed_file_name)

    def get_reconstruct_fastq_path(self, job_index, file_pair_index, file_index):
        decompressed_bin = self.get_decompressed_output_path(job_index, file_pair_index, file_index)
        return decompressed_bin  # No need to add .fastq again, it's already in the decompressed path

    def get_compression_metric_path(self, file_pair_index, file_index):
        input_files = self.config['input_file'][file_pair_index]
        input_file_path = self.get_full_path(input_files[file_index])
        base_filename = os.path.basename(input_file_path)
        metrics_filename = f"compression_metrics_{base_filename}.csv"
        metrics_dir = os.path.abspath(os.path.join(self.project_base_dir, 'Compression_Scripts', 'Logs', 'metrics'))
        self.ensure_directory_exists(metrics_dir)
        return os.path.join(metrics_dir, metrics_filename)

    def get_output_log_path(self, job_index, file_pair_index, file_index, job_type='job'):
        logs_dir = os.path.join(self.project_base_dir, 'Compression_Scripts/Logs/logs')
        self.ensure_directory_exists(logs_dir)
        return os.path.join(logs_dir, f"{job_type}_{file_pair_index}_{job_index}_{file_index}_output.log")

    def get_error_log_path(self, job_index, file_pair_index, file_index, job_type='job'):
        logs_dir = os.path.join(self.project_base_dir, 'Compression_Scripts/Logs/logs')
        self.ensure_directory_exists(logs_dir)
        return os.path.join(logs_dir, f"{job_type}_{file_pair_index}_{job_index}_{file_index}_error.log")

    def get_script_path(self, job_index, file_pair_index, file_index):
        scripts_dir = os.path.join(self.project_base_dir, 'Compression_Scripts/Logs/JobScripts')
        self.ensure_directory_exists(scripts_dir)
        return os.path.join(scripts_dir, f"job_{file_pair_index}_{job_index}_{file_index}.sh")

    def get_pre_processing_script_path(self, job_index, file_pair_index, file_index):
        scripts_dir = os.path.join(self.project_base_dir, 'Compression_Scripts/Logs/JobScripts')
        self.ensure_directory_exists(scripts_dir)
        return os.path.join(scripts_dir, f"fastq_split_{file_pair_index}_{file_index}.sh")

    def get_fastq_reconstruct_script_path(self, job_index, file_pair_index, file_index):
        scripts_dir = os.path.join(self.project_base_dir, 'Compression_Scripts/Logs/JobScripts')
        self.ensure_directory_exists(scripts_dir)
        return os.path.join(scripts_dir, f"fastq_reconstruct_{file_pair_index}_{job_index}_{file_index}.sh")

    def get_pre_processing_output_log_path(self, job_index, file_pair_index, file_index):
        logs_dir = os.path.join(self.project_base_dir, 'Compression_Scripts/Logs/logs')
        self.ensure_directory_exists(logs_dir)
        return os.path.join(logs_dir, f"pre_processing_{file_pair_index}_{file_index}_output.log")

    def get_pre_processing_error_log_path(self, job_index, file_pair_index, file_index):
        logs_dir = os.path.join(self.project_base_dir, 'Compression_Scripts/Logs/logs')
        self.ensure_directory_exists(logs_dir)
        return os.path.join(logs_dir, f"pre_processing_{file_pair_index}_{file_index}_error.log")

    def get_build_pre_processing_cpp_path(self):
        build_path = os.path.join(self.project_base_dir, 'Compression_Scripts', 'build')
        return build_path

    def get_build_fastq_reconstruct_cpp_path(self):
        build_path = os.path.join(self.project_base_dir, 'Compression_Scripts', 'build')
        return build_path

    def get_compressor_name(self, job_index, file_pair_index, file_index):
        job = self.config['jobs'][job_index]
        compressor_name = job['name']
        options = job['options'][0]  # Get the first option for compression
        formatted_options = options.replace(" ", "_")
        return f"{compressor_name}_{formatted_options}"

    # ------------------------------------------------------------------------------------------
    # Post-Hoc Path
    # ------------------------------------------------------------------------------------------

    def get_truth_sam_path(self, job_index, file_pair_index, file_index):
        input_file_path = self.get_input_file_path(job_index, file_pair_index, file_index)
        sam_filename = f"{os.path.basename(input_file_path)}.sam"
        sam_path = os.path.abspath(os.path.join(self.storage_dir, 'SAM', sam_filename))
        self.ensure_directory_exists(os.path.dirname(sam_path))
        return sam_path

    def get_truth_sorted_bam_path(self, job_index, file_pair_index, file_index):
        sam_path = self.get_truth_sam_path(job_index, file_pair_index, file_index)
        bam_filename = f"{os.path.basename(sam_path).replace('.sam', '')}_sorted.bam"
        bam_path = os.path.abspath(os.path.join(self.storage_dir, 'BAM', bam_filename))
        self.ensure_directory_exists(os.path.dirname(bam_path))
        return bam_path

    def get_truth_variant_path(self, job_index, file_pair_index, file_index):
        bam_path = self.get_truth_sorted_bam_path(job_index, file_pair_index, file_index)
        vcf_filename = f"{os.path.basename(bam_path).replace('_sorted.bam', '')}.vcf"
        vcf_path = os.path.abspath(os.path.join(self.storage_dir, 'VCF', vcf_filename))
        self.ensure_directory_exists(os.path.dirname(vcf_path))
        return vcf_path

    def get_truth_compressed_variant_path(self, job_index, file_pair_index, file_index):
        vcf_path = self.get_truth_variant_path(job_index, file_pair_index, file_index)
        compressed_variant_path = vcf_path + '.gz'
        return compressed_variant_path

    def get_sam_path(self, job_index, file_pair_index, file_index):
        input_file_path = self.get_input_file_path(job_index, file_pair_index, file_index)
        job_options = self.config['jobs'][job_index]['options'][0]
        sanitized_options = job_options.replace(" ", "_").replace("/", "_")
        sam_filename = f"{os.path.basename(input_file_path)}_{sanitized_options}.sam"
        sam_path = os.path.abspath(os.path.join(self.storage_dir, 'SAM', sam_filename))
        self.ensure_directory_exists(os.path.dirname(sam_path))
        return sam_path

    def get_sorted_bam_path(self, job_index, file_pair_index, file_index):
        sam_path = self.get_sam_path(job_index, file_pair_index, file_index)
        bam_filename = f"{os.path.basename(sam_path).replace('.sam', '')}_sorted.bam"
        bam_path = os.path.abspath(os.path.join(self.storage_dir, 'BAM', bam_filename))
        self.ensure_directory_exists(os.path.dirname(bam_path))
        return bam_path

    def get_variant_path(self, job_index, file_pair_index, file_index):
        bam_path = self.get_sorted_bam_path(job_index, file_pair_index, file_index)
        vcf_filename = f"{os.path.basename(bam_path).replace('_sorted.bam', '')}.vcf"
        vcf_path = os.path.abspath(os.path.join(self.storage_dir, 'VCF', vcf_filename))
        self.ensure_directory_exists(os.path.dirname(vcf_path))
        return vcf_path

    def get_compressed_variant_path(self, job_index, file_pair_index, file_index):
        vcf_path = self.get_variant_path(job_index, file_pair_index, file_index)
        compressed_variant_path = vcf_path + '.gz'
        return compressed_variant_path

    def get_truth_vcf_script_path(self, job_index, file_pair_index, file_index):
        scripts_dir = os.path.join(self.project_base_dir, 'Post_Hoc_Scripts/Logs/JobScripts')
        self.ensure_directory_exists(scripts_dir)
        return os.path.join(scripts_dir, f"truth_vcf_{file_pair_index}.sh")

    def get_lossy_vcf_script_path(self, job_index, file_pair_index, file_index):
        scripts_dir = os.path.join(self.project_base_dir, 'Post_Hoc_Scripts/Logs/JobScripts')
        self.ensure_directory_exists(scripts_dir)
        return os.path.join(scripts_dir, f"post_hoc_{file_pair_index}_{job_index}_{file_index}.sh")

    def get_vcf_script_path(self, job_index, file_pair_index, file_index):
        scripts_dir = os.path.join(self.project_base_dir, 'Post_Hoc_Scripts/Logs/JobScripts')
        self.ensure_directory_exists(scripts_dir)
        return os.path.join(scripts_dir, f"truth_vcf_{file_pair_index}_{job_index}.sh")

    def get_comparison_dir_path(self, job_index, file_pair_index, file_index):
        comparison_dir = os.path.join(self.storage_dir, 'VCF', 'comparison',
                                      f"{file_pair_index}_{job_index}_{file_index}")
        self.ensure_directory_exists(comparison_dir)
        return comparison_dir

    def get_post_hoc_metric_path(self, file_pair_index, file_index):
        input_files = self.config['input_file'][file_pair_index]
        input_file_path = self.get_full_path(input_files[0])
        base_filename = os.path.basename(input_file_path)
        metrics_filename = f"post_hoc_{base_filename}.csv"
        metrics_dir = os.path.abspath(os.path.join(self.project_base_dir, 'Post_Hoc_Scripts', 'Logs', 'metrics'))
        self.ensure_directory_exists(metrics_dir)
        return os.path.join(metrics_dir, metrics_filename)

    def get_post_hoc_output_log_path(self, job_index, file_pair_index, file_index):
        logs_dir = os.path.join(self.project_base_dir, 'Post_Hoc_Scripts/Logs/logs')
        self.ensure_directory_exists(logs_dir)
        return os.path.join(logs_dir, f"post_hoc_{file_pair_index}_{job_index}_{file_index}_output.log")

    def get_post_hoc_error_log_path(self, job_index, file_pair_index, file_index):
        logs_dir = os.path.join(self.project_base_dir, 'Post_Hoc_Scripts/Logs/logs')
        self.ensure_directory_exists(logs_dir)
        return os.path.join(logs_dir, f"post_hoc_{file_pair_index}_{job_index}_{file_index}_error.log")

    def get_post_hoc_truth_output_log_path(self, job_index, file_pair_index, file_index):
        logs_dir = os.path.join(self.project_base_dir, 'Post_Hoc_Scripts/Logs/logs')
        self.ensure_directory_exists(logs_dir)
        return os.path.join(logs_dir, f"truth_vcf_{file_pair_index}_output.log")

    def get_post_hoc_truth_error_log_path(self, job_index, file_pair_index, file_index):
        logs_dir = os.path.join(self.project_base_dir, 'Post_Hoc_Scripts/Logs/logs')
        self.ensure_directory_exists(logs_dir)
        return os.path.join(logs_dir, f"truth_vcf_{file_pair_index}_error.log")

    # ------------------------------------------------------------------------------------------
    # Error Analysis Path
    # ------------------------------------------------------------------------------------------

    def get_error_analysis_metric_path(self, file_pair_index, file_index):
        input_files = self.config['input_file'][file_pair_index]
        input_file_path = self.get_full_path(input_files[file_index])
        base_filename = os.path.basename(input_file_path)
        metrics_filename = f"error_analysis_metrics_{base_filename}.csv"
        metrics_dir = os.path.abspath(os.path.join(self.project_base_dir, 'Error_Analysis_Scripts', 'Logs', 'metrics'))
        self.ensure_directory_exists(metrics_dir)
        return os.path.join(metrics_dir, metrics_filename)

    def get_error_analysis_script_path(self, job_index, file_pair_index, file_index):
        scripts_dir = os.path.join(self.project_base_dir, 'Error_Analysis_Scripts', 'Logs', 'JobScripts')
        self.ensure_directory_exists(scripts_dir)
        return os.path.join(scripts_dir, f"error_analysis_{file_pair_index}_{job_index}_{file_index}.sh")

    def get_build_cpp_path(self):
        build_path = os.path.join(self.project_base_dir, 'Error_Analysis_Scripts', 'build')
        return build_path

    def get_error_analysis_output_log_path(self, job_index, file_pair_index, file_index):
        logs_dir = os.path.join(self.project_base_dir, 'Error_Analysis_Scripts/Logs/logs')
        self.ensure_directory_exists(logs_dir)
        return os.path.join(logs_dir, f"error_analysis_{file_pair_index}_{job_index}_{file_index}_output.log")

    def get_error_analysis_error_log_path(self, job_index, file_pair_index, file_index):
        logs_dir = os.path.join(self.project_base_dir, 'Error_Analysis_Scripts/Logs/logs')
        self.ensure_directory_exists(logs_dir)
        return os.path.join(logs_dir, f"post_hoc_{file_pair_index}_{job_index}_{file_index}_error.log")


if __name__ == "__main__":
    config_path = "../Jobs/bfqzip.json"  # Adjust the path as necessary
    pg = PathGenerator(config_path)
    job_index = 0
    file_pair_index = 0  # example file pair index
    file_index = 0  # example file index
    try:
        print(pg.get_compressed_output_path(job_index, file_pair_index, file_index))
        print(pg.get_decompressed_output_path(job_index, file_pair_index, file_index))
    except Exception as e:
        print(f"Error: {e}")
