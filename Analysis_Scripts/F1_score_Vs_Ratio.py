import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("./Metrics/ERR016126.csv")

# Extract the baseline F1 score
base_line = df[df['Compressor_Name'] == 'spring_-c_-l_-q_ill_bin']
base_line_f1 = base_line['F1_Score']

# Initialize lists to store tuples of (compression ratio, f1_score)
fqzcomp = []
SZ3 = []
SPRING = []
BFQzip = []

# Function to add data to the corresponding list
def add_to_list(compressor_name, ratio, f1_score):
    if 'fqzcomp' in compressor_name:
        fqzcomp.append((ratio, f1_score))
    elif 'SZ3' in compressor_name:
        SZ3.append((ratio, f1_score))
    elif 'spring' in compressor_name:
        SPRING.append((ratio, f1_score))
    elif 'BFQzip' in compressor_name:
        BFQzip.append((ratio, f1_score))

# Read the CSV file line by line
with open("./Analysis_Scripts/Metrics/ERR016126.csv", 'r') as file:
    # Skip the header
    next(file)
    for line in file:
        parts = line.strip().split(',')
        compressor_name = parts[1]
        if compressor_name == 'spring_-c_-l_-q_ill_bin':
            continue  # Skip the baseline
        ratio = float(parts[6])
        f1_score = float(parts[15])
        add_to_list(compressor_name, ratio, f1_score)

# Plotting the data
plt.figure(figsize=(10, 6))

# Plot data for each compressor
for name, data in [('fqzcomp', fqzcomp), ('SZ3', SZ3), ('SPRING', SPRING), ('BFQzip', BFQzip)]:
    if data:  # Ensure there's data to plot
        ratios, f1_scores = zip(*data)
        plt.scatter(ratios, f1_scores, label=name)

# Add labels and legend
plt.xlabel('Compression Ratio')
plt.ylabel('F1 Score')
plt.title('Compression Ratio vs F1 Score for Different Compressors')
plt.legend()
plt.grid(True)
plt.show()
