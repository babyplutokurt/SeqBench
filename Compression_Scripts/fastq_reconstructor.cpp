#include <iostream>
#include <fstream>
#include <string>
#include <stdexcept>
#include <vector>
#include <cstdint>
#include <cmath>

void fastq_reconstructor(const std::string& base_identifiers_path,
                         const std::string& dna_bases_path,
                         const std::string& quality_identifiers_path,
                         const std::string& quality_scores_path,
                         const std::string& output_path) {
    std::ifstream base_identifiers_file(base_identifiers_path);
    std::ifstream dna_bases_file(dna_bases_path);
    std::ifstream quality_identifiers_file(quality_identifiers_path);
    std::ifstream quality_scores_file(quality_scores_path, std::ios::binary);
    std::ofstream output_file(output_path);

    if (!base_identifiers_file.is_open() || !dna_bases_file.is_open() ||
        !quality_identifiers_file.is_open() || !quality_scores_file.is_open() ||
        !output_file.is_open()) {
        throw std::runtime_error("Unable to open input or output files.");
    }

    std::string base_identifier, dna_bases, quality_identifier;
    while (std::getline(base_identifiers_file, base_identifier) &&
           std::getline(dna_bases_file, dna_bases) &&
           std::getline(quality_identifiers_file, quality_identifier)) {

        // Write the base identifier to the output file
        output_file << base_identifier << "\n";
        // Write the dna bases to the output file
        output_file << dna_bases << "\n";
        // Write the quality identifier to the output file
        output_file << quality_identifier << "\n";

        // Read the quality scores corresponding to the dna_bases length
        std::vector<float> quality_scores(dna_bases.size());
        quality_scores_file.read(reinterpret_cast<char*>(quality_scores.data()), quality_scores.size() * sizeof(float));

        // Convert the float quality scores back to characters and write to output file
        for (float score : quality_scores) {
            int int_score = std::round(score);  // Round to nearest integer
            if (int_score < 2) int_score = 2;   // Minimum value is 2
            char qual_char = static_cast<char>(int_score + 33); // Convert to char
            output_file << qual_char;
        }
        output_file << "\n";
    }

    base_identifiers_file.close();
    dna_bases_file.close();
    quality_identifiers_file.close();
    quality_scores_file.close();
    output_file.close();
}
