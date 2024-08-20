#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "fastq_metrics.cpp"

namespace py = pybind11;

PYBIND11_MODULE(fastq_metrics, m
) {
m.def("read_quality_scores", &read_quality_scores, "Read quality scores from a FastQ file");
m.def("calculate_mse_psnr", &calculate_mse_psnr, "Calculate Mean Squared Error (MSE) and Peak Signal-to-Noise Ratio (PSNR)");
m.def("calculate_mse_psnr_v2", &calculate_mse_psnr_v2, "Calculate MSE and PSNR directly from files without loading all quality scores into memory");
m.def("calculate_mse_psnr_v3", &calculate_mse_psnr_v3, "Calculate MSE and PSNR directly from files without loading all quality scores into memory, with multithreading support", py::arg("original_filename"), py::arg("decompressed_filename"), py::arg("threads"));
}
