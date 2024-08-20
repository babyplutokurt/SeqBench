cmake_minimum_required(VERSION 3.4...3.18)
project(fastq_metrics)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(pybind11 REQUIRED)

add_library(fastq_metrics MODULE fastq_metrics_bindings.cpp)
target_link_libraries(fastq_metrics PRIVATE pybind11::module)
# Set the module output directory
set_target_properties(fastq_metrics PROPERTIES PREFIX "" SUFFIX ".so")
