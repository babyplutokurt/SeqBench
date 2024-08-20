cmake_minimum_required(VERSION 3.4)
project(fastq_processor)

set(CMAKE_CXX_STANDARD 14)

# If using the submodule method:
# add_subdirectory(pybind11)
# add_subdirectory(mio)

# If using the package method:
find_package(pybind11 REQUIRED)

add_library(fastq_processor_core STATIC fastq_processor.cpp fastq_reconstructor.cpp)
set_target_properties(fastq_processor_core PROPERTIES POSITION_INDEPENDENT_CODE ON)

pybind11_add_module(fastq_processor fastq_processor_bindings.cpp)
target_link_libraries(fastq_processor PRIVATE fastq_processor_core)

pybind11_add_module(fastq_reconstructor fastq_reconstructor_bindings.cpp)
target_link_libraries(fastq_reconstructor PRIVATE fastq_processor_core)

# Include mio headers
target_include_directories(fastq_processor_core PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/mio/include)
