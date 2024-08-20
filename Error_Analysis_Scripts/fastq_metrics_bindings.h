// fastq_metrics_bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "fastq_metrics.cpp"

namespace py = pybind11;

PYBIND11_MODULE(fastq_metrics, m) {
m.def("read_quality_scores", &read_quality_scores, "Read quality scores from a FastQ file");
m.def("calculate_mse_psnr", &calculate_mse_psnr, "Calculate Mean Squared Error (MSE) and Peak Signal-to-Noise Ratio (PSNR)");
}
