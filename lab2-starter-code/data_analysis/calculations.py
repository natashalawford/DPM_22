import sys
import statistics

def analyze_file(filename):
    try:
        # Read all values from the file, one per line
        with open(filename, "r") as f:
            values = [float(line.strip()) for line in f if line.strip()]

        if not values:
            print("The file is empty.")
            return

        # Compute stats
        minimum = min(values)
        maximum = max(values)
        mean = statistics.mean(values)
        stdev = statistics.pstdev(values)  # population stdev (use stdev() for sample)

        # Print results
        print(f"Count: {len(values)}")
        print(f"Min: {minimum}")
        print(f"Max: {maximum}")
        print(f"Mean: {mean:.4f}")
        print(f"Standard Deviation: {stdev:.4f}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except ValueError:
        print("Error: File contains non-numeric values.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <filename>")
    else:
        analyze_file(sys.argv[1])
