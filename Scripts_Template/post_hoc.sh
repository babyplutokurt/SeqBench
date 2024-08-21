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

# Step 1: Index the reference fasta file (if not already indexed)
if [ ! -f {{ reference_file }}.bwt ]; then
    bwa index {{ reference_file }}
fi

# Step 2: Alignment
bwa mem -t {{ threads }} {{ reference_file }} {{ input_fastq_1 }} {{ input_fastq_2 }} > {{ sam_path }}

# Step 3: Convert SAM to BAM, sort, and index
samtools view -bS {{ sam_path }} | samtools sort -@ {{ threads }} -o {{ sorted_bam_path }}
samtools index --threads {{ threads }} {{ sorted_bam_path }}

# Step 4: Call variants using bcftools
bcftools mpileup --threads {{ threads }} -f {{ reference_file }} {{ sorted_bam_path }} | bcftools call -mv -Ov -o {{ variant_path }}

# Step 5: Compress and index the new VCF file
bgzip --threads {{ threads }} -c {{ variant_path }} > {{ compressed_variant_path }}
tabix --threads {{ threads }} -p vcf {{ compressed_variant_path }}

# Step 6: Compare the new VCF file with the original VCF file
bcftools isec --threads {{ threads }}  -p {{ comparison_dir }} -Oz {{ original_vcf }} {{ compressed_variant_path }}

# Step 7: Calculate precision, recall, and F1 score
TP=$(bcftools view {{ comparison_dir }}/0002.vcf.gz | grep -v '^#' | wc -l)
FP=$(bcftools view {{ comparison_dir }}/0001.vcf.gz | grep -v '^#' | wc -l)
FN=$(bcftools view {{ comparison_dir }}/0000.vcf.gz | grep -v '^#' | wc -l)

precision=$(echo "scale=6; $TP / ($TP + $FP)" | bc)
recall=$(echo "scale=6; $TP / ($TP + $FN)" | bc)
f1_score=$(echo "scale=6; 2 * ($precision * $recall) / ($precision + $recall)" | bc)

echo "Precision: $precision"
echo "Recall: $recall"
echo "F1 Score: $f1_score"


echo "{{ job_name }},{{ compressor_name }},$TP, $FP, $FN, $precision, $recall, $f1_score" >> "{{ metrics_csv_path }}"

# Deactivate the conda environment
conda deactivate
