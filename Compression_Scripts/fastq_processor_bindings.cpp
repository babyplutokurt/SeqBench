#include <pybind11/pybind11.h>
#include <cstdint>

// Declare the function from the other file
void process_fastq(const std::string& input_path,
                   const std::string& base_identifiers_path,
                   const std::string& dna_bases_path,
                   const std::string& quality_identifiers_path,
                   const std::string& quality_scores_path,
                   std::uint64_t buffer_size);

namespace py = pybind11;

PYBIND11_MODULE(fastq_processor, m) {
m.def("process_fastq", &process_fastq, "A function to process FASTQ files and split contents into four separate files.",
py::arg("input_path"), py::arg("base_identifiers_path"), py::arg("dna_bases_path"),
py::arg("quality_identifiers_path"), py::arg("quality_scores_path"),
py::arg("buffer_size") = static_cast<std::uint64_t>(10) * 1024 * 1024 * 1024); // Default to 10GB
}
