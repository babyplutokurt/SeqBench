#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <string>
#include <thread>
#include <mutex>
#include <utility>
#include <stdexcept>

// Original functions
std::vector<int> read_quality_scores(const std::string& filename) {
    std::ifstream file(filename);
    std::vector<int> quality_scores;
    std::string line;
    int line_count = 0;

    while (std::getline(file, line)) {
        line_count++;
        if (line_count % 4 == 0) {
            for (char c : line) {
                quality_scores.push_back(static_cast<int>(c) - 33);
            }
        }
    }

    file.close();
    return quality_scores;
}

std::pair<double, double> calculate_mse_psnr(const std::vector<int>& original, const std::vector<int>& decompressed) {
    if (original.size() != decompressed.size()) {
        throw std::invalid_argument("The two files must have the same number of quality scores");
    }

    double mse = 0.0;
    double max_i = 40.0;
    for (size_t i = 0; i < original.size(); ++i) {
        mse += std::pow(original[i] - decompressed[i], 2);
    }
    mse /= original.size();

    double psnr = mse == 0 ? std::numeric_limits<double>::infinity() : 10 * std::log10((max_i * max_i) / mse);

    return {mse, psnr};
}

// v2 function
std::pair<double, double> calculate_mse_psnr_v2(const std::string& original_filename, const std::string& decompressed_filename) {
    std::ifstream original_file(original_filename);
    std::ifstream decompressed_file(decompressed_filename);

    if (!original_file.is_open() || !decompressed_file.is_open()) {
        throw std::runtime_error("Failed to open one or both files");
    }

    std::string original_line, decompressed_line;
    int line_count = 0;
    double mse = 0.0;
    double max_i = 40.0;
    size_t score_count = 0;

    while (std::getline(original_file, original_line) && std::getline(decompressed_file, decompressed_line)) {
        line_count++;
        if (line_count % 4 == 0) {
            if (original_line.length() != decompressed_line.length()) {
                throw std::invalid_argument("The two files must have the same number of quality scores per record");
            }
            for (size_t i = 0; i < original_line.length(); ++i) {
                int original_score = static_cast<int>(original_line[i]) - 33;
                int decompressed_score = static_cast<int>(decompressed_line[i]) - 33;
                mse += std::pow(original_score - decompressed_score, 2);
                score_count++;
            }
        }
    }

    mse /= score_count;
    double psnr = mse == 0 ? std::numeric_limits<double>::infinity() : 10 * std::log10((max_i * max_i) / mse);

    original_file.close();
    decompressed_file.close();

    return {mse, psnr};
}

// Helper function for processing chunks
void process_chunk(const std::string& original_filename, const std::string& decompressed_filename, size_t start_line, size_t end_line,
                   double& mse, size_t& score_count, std::mutex& mtx) {
    std::ifstream original_file(original_filename);
    std::ifstream decompressed_file(decompressed_filename);

    if (!original_file.is_open() || !decompressed_file.is_open()) {
        throw std::runtime_error("Failed to open one or both files");
    }

    std::string original_line, decompressed_line;
    size_t line_number = 0;
    size_t local_score_count = 0;
    double local_mse = 0.0;

    while (std::getline(original_file, original_line) && std::getline(decompressed_file, decompressed_line)) {
        line_number++;
        if (line_number < start_line || line_number > end_line) {
            continue;
        }
        if (line_number % 4 == 0) { // Process only the quality score lines (every 4th line)
            if (original_line.length() != decompressed_line.length()) {
                throw std::invalid_argument("The two files must have the same number of quality scores per record");
            }
            // Process each character in the quality score line
            for (size_t i = 0; i < original_line.length(); ++i) {
                int original_score = static_cast<int>(original_line[i]) - 33; // Convert ASCII to quality score
                int decompressed_score = static_cast<int>(decompressed_line[i]) - 33; // Convert ASCII to quality score
                local_mse += std::pow(original_score - decompressed_score, 2);
                local_score_count++;
            }
        }
    }

    // Update shared variables with thread-safe operations
    std::lock_guard<std::mutex> lock(mtx);
    mse += local_mse;
    score_count += local_score_count;
}

// v3 function with multithreading support and correct chunk processing
std::pair<double, double> calculate_mse_psnr_v3(const std::string& original_filename, const std::string& decompressed_filename, int threads) {
    std::ifstream original_file(original_filename);

    if (!original_file.is_open()) {
        throw std::runtime_error("Failed to open the original file");
    }

    size_t total_lines = 0;
    std::string line;

    // Count total lines in the original file
    while (std::getline(original_file, line)) {
        total_lines++;
    }

    if (total_lines % 4 != 0) {
        throw std::invalid_argument("The total number of lines in the file must be a multiple of 4");
    }

    size_t total_records = total_lines / 4;
    size_t records_per_thread = total_records / threads;
    size_t lines_per_thread = records_per_thread * 4;

    double mse = 0.0;
    size_t score_count = 0;
    std::mutex mtx;

    std::vector<std::thread> thread_pool;

    for (int i = 0; i < threads; ++i) {
        size_t start_line = i * lines_per_thread + 1;
        size_t end_line = (i == threads - 1) ? total_lines : (i + 1) * lines_per_thread;

        thread_pool.emplace_back(process_chunk, original_filename, decompressed_filename, start_line, end_line, std::ref(mse), std::ref(score_count), std::ref(mtx));
    }

    for (auto& t : thread_pool) {
        t.join();
    }

    mse /= score_count;
    double max_i = 40.0;
    double psnr = mse == 0 ? std::numeric_limits<double>::infinity() : 10 * std::log10((max_i * max_i) / mse);

    return {mse, psnr};
}
