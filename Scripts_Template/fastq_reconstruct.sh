#!/bin/sh
#PBS -l walltime={{ walltime }}
#PBS -N {{ job_name }}
#PBS -l nodes={{ nodes }}:ppn={{ ppn }}
#PBS -M {{ email }}
#PBS -o {{ output_log }}
#PBS -e {{ error_log }}

{{ dependency_line }}

# Change to directory where 'qsub' was called
cd $PBS_O_WORKDIR

source {{ conda_path }} compression

# Start reconstruction
python -c "import sys
sys.path.append('{{ get_build_pre_processing_cpp_path }}')
import fastq_reconstructor; fastq_reconstructor.fastq_reconstructor('{{ output_bases_id_path }}', '{{ output_bases_path }}', '{{ output_quality_id_path }}', '{{ output_quality_path }}', '{{ output_path }}')"

conda deactivate
