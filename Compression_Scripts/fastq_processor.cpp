#include <iostream>
#include <fstream>
#include <string>
#include <stdexcept>
#include <vector>
#include <sstream>
#include <cstdint>

void process_fastq(const std::string& input_path,
                   const std::string& base_identifiers_path,
                   const std::string& dna_bases_path,
                   const std::string& quality_identifiers_path,
                   const std::string& quality_scores_path,
                   std::uint64_t buffer_size = static_cast<std::uint64_t>(10) * 1024 * 1024 * 1024) { // 10GB buffer size

    std::ifstream infile(input_path);
    std::ofstream base_identifiers_file(base_identifiers_path);
    std::ofstream dna_bases_file(dna_bases_path);
    std::ofstream quality_identifiers_file(quality_identifiers_path);
    std::ofstream quality_scores_file(quality_scores_path, std::ios::binary);

    if (!infile.is_open() || !base_identifiers_file.is_open() ||
        !dna_bases_file.is_open() || !quality_identifiers_file.is_open() ||
        !quality_scores_file.is_open()) {
        throw std::runtime_error("Unable to open input or output files.");
    }

    std::ostringstream base_identifiers_buffer;
    std::ostringstream dna_bases_buffer;
    std::ostringstream quality_identifiers_buffer;
    std::vector<float> quality_scores_buffer;

    // std::uint64_t quality_scores_count = 0;
    // std::uint64_t max_quality_scores_count = (9ULL * 1024 * 1024 * 1024) / sizeof(float); // 9GB buffer for quality scores

    std::string base_identifier, dna_bases, quality_identifier, quality_scores;
    int lines_read = 0;
    const int max_lines = 500000;

    while (std::getline(infile, base_identifier) &&
           std::getline(infile, dna_bases) &&
           std::getline(infile, quality_identifier) &&
           std::getline(infile, quality_scores)) {

        base_identifiers_buffer << base_identifier << "\n";
        dna_bases_buffer << dna_bases << "\n";
        quality_identifiers_buffer << quality_identifier << "\n";

        for (char c : quality_scores) {
            float quality_score = static_cast<float>(c) - 33;
            quality_scores_buffer.push_back(quality_score);
        }

        lines_read += 4; // Each record is 4 lines

        if (lines_read >= max_lines) {
            base_identifiers_file << base_identifiers_buffer.str();
            dna_bases_file << dna_bases_buffer.str();
            quality_identifiers_file << quality_identifiers_buffer.str();
            quality_scores_file.write(reinterpret_cast<const char*>(quality_scores_buffer.data()), quality_scores_buffer.size() * sizeof(float));

            base_identifiers_buffer.str("");
            base_identifiers_buffer.clear();
            dna_bases_buffer.str("");
            dna_bases_buffer.clear();
            quality_identifiers_buffer.str("");
            quality_identifiers_buffer.clear();
            quality_scores_buffer.clear();

            lines_read = 0;
            // quality_scores_count = 0;
        }
    }

    // Write any remaining data
    if (!quality_scores_buffer.empty()) {
        quality_scores_file.write(reinterpret_cast<const char*>(quality_scores_buffer.data()), quality_scores_buffer.size() * sizeof(float));
    }
    if (base_identifiers_buffer.tellp() > 0) {
        base_identifiers_file << base_identifiers_buffer.str();
    }
    if (dna_bases_buffer.tellp() > 0) {
        dna_bases_file << dna_bases_buffer.str();
    }
    if (quality_identifiers_buffer.tellp() > 0) {
        quality_identifiers_file << quality_identifiers_buffer.str();
    }

    infile.close();
    base_identifiers_file.close();
    dna_bases_file.close();
    quality_identifiers_file.close();
    quality_scores_file.close();
}
