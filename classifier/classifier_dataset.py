import json
import pandas as pd

def process_file(filename, output_status):
    results = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()  # Remove whitespace, including newline
            if line:  # Ensure the line is not empty
                results.append({
                    'instruction': line,
                    'output': output_status
                })
    return results

def main():
    pass_data = process_file('pass.txt', 'pass')
    fail_data = process_file('fail.txt', 'fail')
    
    # Combine the two datasets
    combined_data = pass_data + fail_data
    
    # Save as JSON
    with open('dataset.json', 'w') as json_file:
        json.dump(combined_data, json_file, indent=4)
    
    # Convert to DataFrame and save as Parquet
    df = pd.DataFrame(combined_data)
    df.to_parquet('dataset.parquet', index=False)

if __name__ == '__main__':
    main()
