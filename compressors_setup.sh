#!/bin/bash

# Create the Compressors directory if it doesn't exist
mkdir -p Compressors

# Array to hold the names of compressors that fail to compile
failed_compressors=()

# Function to compile a compressor
compile_compressor() {
    local repo_url=$1
    local dir_name=$2
    local build_commands=$3
    local clone_options=$4

    # Navigate to the Compressors directory
    cd Compressors

    # Clone the repository if it doesn't already exist
    if [ ! -d "$dir_name" ]; then
        echo "Cloning repository: $repo_url"
        git clone $clone_options "$repo_url" "$dir_name"
    else
        echo "Directory $dir_name already exists, skipping clone."
    fi

    # Navigate to the compressor directory and compile
    cd "$dir_name" || { echo "Failed to navigate to directory: $dir_name"; failed_compressors+=("$dir_name"); cd ../..; return 1; }
    echo "Building $dir_name..."
    eval "$build_commands" || { echo "Compilation of $dir_name failed!"; failed_compressors+=("$dir_name"); cd ../..; return 1; }

    # Return to the base directory
    cd ../..
}

# Compile fqzcomp compressor
compile_compressor "https://github.com/jkbonfield/fqzcomp.git" "fqzcomp" "make"

# Compile spring compressor
compile_compressor "https://github.com/shubhamchandak94/SPRING.git" "SPRING" "mkdir -p build && cd build && cmake .. && make"

# Compile RENANO compressor
compile_compressor "https://github.com/guilledufort/RENANO.git" "RENANO" "cd renano && make"

# Compile Enano compressor
compile_compressor "https://github.com/guilledufort/EnanoFASTQ.git" "EnanoFASTQ" "cd enano && make"

# Compile BFQZIP compressor (with recursive submodule cloning)
compile_compressor "https://github.com/veronicaguerrini/BFQzip" "BFQzip" "make" "--recursive"

# Compile SZ3 compressor
compile_compressor "https://github.com/szcompressor/SZ3.git" "SZ3" "mkdir -p build && cd build && cmake -DCMAKE_INSTALL_PREFIX:PATH=$PWD .. && make && make install"

echo "All compressors have been processed."

# Check if any compressors failed
if [ ${#failed_compressors[@]} -eq 0 ]; then
    echo "All compressors compiled successfully!"
else
    echo "The following compressors failed to compile:"
    for compressor in "${failed_compressors[@]}"; do
        echo "- $compressor"
    done
fi
