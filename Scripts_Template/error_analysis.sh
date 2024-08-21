#!/bin/sh
#PBS -l walltime={{ walltime }}
#PBS -N {{ job_name }}
#PBS -q {{ node_size }}
#PBS -l nodes={{ nodes }}:ppn={{ ppn }}
#PBS -M {{ email }}
#PBS -o {{ output_log }}
#PBS -e {{ error_log }}

{{ dependency_line }}

# Change to the working directory
cd $PBS_O_WORKDIR

source {{ conda_path }} compression

# Run error analysis using the fastq_metrics API
mse_psnr_output=$(python3 -c "
import sys
sys.path.append('{{ build_cpp_path }}')
import fastq_metrics
original_file = '{{ original_file }}'
decompressed_file = '{{ decompressed_file }}'
threads = {{ threads }}
mse_v3, psnr_v3 = fastq_metrics.calculate_mse_psnr_v3(original_file, decompressed_file, threads)
print(f'{mse_v3},{psnr_v3}')
")

# Extract MSE and PSNR values
mse_v3=$(echo $mse_psnr_output | cut -d',' -f1)
psnr_v3=$(echo $mse_psnr_output | cut -d',' -f2)

# Write the results to the CSV file
echo "{{ job_name }},{{ compressor_name }},$mse_v3,$psnr_v3" >> "{{ metrics_csv_path }}"

conda deactivate
