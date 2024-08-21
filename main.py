import sys
import os

sys.path.append('./')
sys.path.append('./Compression_Scripts')
sys.path.append('./Post_Hoc_Scripts')
from Compression_Scripts.job_generator import JobGenerator
from Post_Hoc_Scripts.post_hoc_analysis import PostHocAnalysis
from Error_Analysis_Scripts.error_analysis import ErrorAnalysis


if __name__ == '__main__':
    pwd = os.getcwd()
    config = pwd + '/Jobs/sample.json'
    fastq_split_template = pwd + '/Scripts_Template/fastq_split.sh'
    fastq_reconstruct_template = pwd + '/Scripts_Template/fastq_reconstruct.sh'
    compression_template = pwd + '/Scripts_Template/compression.sh'
    error_analysis_template = pwd + '/Scripts_Template/error_analysis.sh'
    truth_vcf_template = pwd + '/Scripts_Template/truth_vcf.sh'
    post_hoc_template = pwd + '/Scripts_Template/post_hoc.sh'

    jb = JobGenerator(config, compression_template, fastq_split_template, fastq_reconstruct_template)
    jb.generate_and_submit_jobs()
    ea = ErrorAnalysis(config, error_analysis_template)
    ea.run_error_analysis()
    pa = PostHocAnalysis(config,  truth_vcf_template, post_hoc_template)
    pa.run_posthoc_analysis()
