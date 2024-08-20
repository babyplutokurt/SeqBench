#include <pybind11/pybind11.h>

void fastq_reconstructor(const std::string& base_identifiers_path,
                         const std::string& dna_bases_path,
                         const std::string& quality_identifiers_path,
                         const std::string& quality_scores_path,
                         const std::string& output_path);

namespace py = pybind11;

PYBIND11_MODULE(fastq_reconstructor, m) {
m.def("fastq_reconstructor", &fastq_reconstructor, "A function to reconstruct FASTQ files from parts");
}
