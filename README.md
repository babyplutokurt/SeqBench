# SeqBench: A Benchmark Suite for Lossless and Lossy Compression of Sequence Data

  

SeqBench, an open-source comprehensive plug-and-play benchmark suite for evaluating both lossless and lossy compression algorithms for DNA sequence data on HPC clusters. SeqBench supports a wide range of compressors, including reference-based and non-reference-based methods, and integrates error analysis using different metrics. SeqBench also incorporates downstream workflow analysis, such as genetic variant calling, to ensure compressed data remains suitable for critical applications.

  


  

### System Requirements

  

- ****Operating System****: Linux (with support for PBS/Torque or Slurm Workload Manager)

- ****Compiler****: GCC (>= 4.8.5)

- ****Python****: Python 3.12 (or compatible version)

- ****Conda****: Miniconda or Anaconda installed

  

### Setting Up the Environment

  

SeqBench comes with a pre-configured `environment.yaml` file that specifies all necessary dependencies. To set up the environment, follow these steps:

  

1. ****Install Conda****: If you don’t have Conda installed, you can install Miniconda by following the instructions [here](https://docs.conda.io/en/latest/miniconda.html).

  

2. ****Create the SeqBench Environment****:

Navigate to the SeqBench directory where `environment.yaml` is located and run the following command:

  

```bash

conda env create -f environment.yaml

```
### Compile

Please use the following command to compile necessary C++ and Cpython module . 

```bash
git clone https://github.com/babyplutokurt/SeqBench

cd Compression_Scripts && mkdir build && cd build
cmake ..
make

cd ../.. && cd Error_Analysis_Scripts && mkdir build && cd build
cmake ..
make
```

Please use the following command to compile compressors 
```bash
```

## Configuration


## Run SeqBench

```bash 
conda activate compression
python3 main.py





