#!/bin/sh
#PBS -l walltime={{ walltime }}
#PBS -N {{ job_name }}
#PBS -l nodes={{ nodes }}:ppn={{ ppn }}
#PBS -M {{ email }}
#PBS -o {{ output_log }}
#PBS -e {{ error_log }}

{{ dependency_line }}

cd $PBS_O_WORKDIR

source {{ conda_path }} compression

python -c "import sys
import json
import os
sys.path.append('{{ get_build_pre_processing_cpp_path }}')
import fastq_processor

# Process the FASTQ file
fastq_processor.process_fastq('{{ input_path }}', '{{ output_bases_id_path }}', '{{ output_bases_path }}', '{{ output_quality_id_path }}', '{{ output_quality_path }}')

# Compress the output files
os.system(f'gzip -9 -k {{ output_bases_id_path }}')
os.system(f'gzip -9 -k {{ output_bases_path }}')

# Get the compressed file sizes
compressed_bases_id_size = os.path.getsize('{{ output_bases_id_path }}.gz')
compressed_bases_size = os.path.getsize('{{ output_bases_path }}.gz')

# Prepare the size data to be written to the JSON file
size_data = {
    '{{ input_path }}': {
        'compressed_bases_id_size': compressed_bases_id_size,
        'compressed_bases_size': compressed_bases_size
    }
}

# Path to the JSON file
json_file_path = '/home/tus53997/SeqBench2/field_size.json'

# Read existing data from the JSON file, if it exists and is valid
try:
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = {}
except (json.JSONDecodeError, FileNotFoundError):
    existing_data = {}

# Update the existing data with the new size data
existing_data.update(size_data)

# Write the updated data back to the JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(existing_data, json_file, indent=4)
"

conda deactivate
