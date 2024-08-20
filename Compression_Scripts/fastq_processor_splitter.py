import csv
import json
import os
import subprocess
import logging
from jinja2 import Template
import sys
import time

sys.path.append('../')
sys.path.append(os.path.join(os.path.dirname(__file__), 'build'))
import fastq_processor
import fastq_reconstructor

input_path = ""
base_identifiers_path = ""
dna_bases_path = ""
quality_identifiers_path = ""
quality_scores_path = ""
output_path = ""

start = time.time()
fastq_processor.process_fastq(input_path, base_identifiers_path, dna_bases_path, quality_identifiers_path, quality_scores_path)
end = time.time()

print(f"FASTQ file processing completed successfully in {end - start} seconds")
