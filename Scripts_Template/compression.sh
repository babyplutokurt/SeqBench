#!/bin/sh
#PBS -l walltime={{ walltime }}
#PBS -N {{ job_name }}
#PBS -q {{ node_size }}
#PBS -l nodes={{ nodes }}:ppn={{ ppn }}
#PBS -M {{ email }}
#PBS -o {{ output_log }}
#PBS -e {{ error_log }}

{{ dependency_line }}

# Change to directory where 'qsub' was called
cd $PBS_O_WORKDIR

source {{ conda_path }} compression

BINARY_LENGTH=$(($(stat -c %s "{{ binary_input_file }}") / 4))

get_time() {
    echo $(date +%s.%N)
}

# Run compression and capture metrics
START_TIME=$(get_time)

{{ reference_command }}
{{ compression_command }}

END_TIME=$(get_time)
COMPRESSION_DURATION=$(echo "$END_TIME - $START_TIME" | bc)

INPUT_SIZE_BYTES=$(stat -c %s "{{ input_path }}")
OUTPUT_SIZE_BYTES=$(stat -c %s "{{ compressed_output_path }}")
INPUT_SIZE_MB=$(echo "scale=6; $INPUT_SIZE_BYTES / 1048576" | bc)
OUTPUT_SIZE_MB=$(echo "scale=6; $OUTPUT_SIZE_BYTES / 1048576" | bc)

# Conditionally calculate the ratio for SZ3 compressor
if [ "{{ compressor }}" = "SZ3" ]; then
    # Load the compressed sizes from the JSON file
    compressed_bases_id_size=$(python -c "import json; data=json.load(open('./field_size.json')); print(data['{{ input_path }}']['compressed_bases_id_size'])")
    compressed_bases_size=$(python -c "import json; data=json.load(open('./field_size.json')); print(data['{{ input_path }}']['compressed_bases_size'])")
    TOTAL_COMPRESSED_SIZE_MB=$(echo "scale=6; ($compressed_bases_id_size + $compressed_bases_size) / 1048576 + $OUTPUT_SIZE_MB" | bc)
    RATIO=$(echo "scale=6; $INPUT_SIZE_MB / $TOTAL_COMPRESSED_SIZE_MB" | bc)
elif [ "{{ compressor }}" = "BFQZIP" ]; then
    fq_dna_size=$(stat -c %s "{{ compressed_output_path }}.fq.dna.7z")
    fq_qs_size=$(stat -c %s "{{ compressed_output_path }}.fq.qs.7z")
    fq_h_size=$(stat -c %s "{{ compressed_output_path }}.h.7z")
    TOTAL_COMPRESSED_SIZE_BYTES=$(echo "$fq_dna_size + $fq_qs_size + $fq_h_size" | bc)
    TOTAL_COMPRESSED_SIZE_MB=$(echo "scale=6; $TOTAL_COMPRESSED_SIZE_BYTES / 1048576" | bc)
    RATIO=$(echo "scale=6; $INPUT_SIZE_MB / $TOTAL_COMPRESSED_SIZE_MB" | bc)
else
    RATIO=$(echo "scale=6; $INPUT_SIZE_MB / $OUTPUT_SIZE_MB" | bc)
fi

COMPRESSION_THROUGHPUT=$(echo "scale=6; $INPUT_SIZE_MB / $COMPRESSION_DURATION" | bc)

sleep 3

# Run decompression and capture metrics
START_TIME=$(get_time)

{{ decompression_command }}

END_TIME=$(get_time)
DECOMPRESSION_DURATION=$(echo "$END_TIME - $START_TIME" | bc)
DECOMPRESSION_THROUGHPUT=$(echo "scale=6; $INPUT_SIZE_MB / $DECOMPRESSION_DURATION" | bc)

echo "{{ job_name }},{{ compressor_name }},$COMPRESSION_DURATION,$COMPRESSION_THROUGHPUT,$DECOMPRESSION_DURATION,$DECOMPRESSION_THROUGHPUT,$RATIO" >> "{{ metrics_csv_path }}"

conda deactivate
