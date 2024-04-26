import os
import re
import csv
import hashlib

source_directory = './data/Kotlin_files'
target_csv_path = './kotlin_functions_dataset.csv'

def extract_kotlin_functions(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()

    pattern = r"""
        ((\s*/\*\*[\s\S]*?\*/)?      # Optional block comment before function
        (\s*//.*\n)*)                 # Optional single line comments before function
        \s*                           # Optional whitespace
        ([\s\S]*?)                    # Capture any text (annotations, modifiers) before the function declaration
        (fun\s+[\s\S]*?(?:\{[\s\S]*?\}|=\s*.+?);?)  # Function declaration
    """

    matches = re.findall(pattern, file_content, re.VERBOSE)
    functions_data = []

    for match in matches:
        comment_block, _, _, preamble, function_declaration = match
        comment_block = comment_block.strip()
        function_signature = re.search(r'fun\s+[\w<>,\s]*\([\w<>,:\s]*\)', function_declaration)
        if function_signature:
            function_signature = function_signature.group(0)
        else:
            function_signature = "No signature found"

        function_body = function_declaration.replace(function_signature, '')
        function_id = hashlib.md5(function_signature.encode('utf-8')).hexdigest()[:4]

        functions_data.append({
            'signature': function_signature,
            'body': function_body.strip(),
            'docstring': comment_block,
            'id': function_id
        })

    return functions_data

# Write the dataset to a CSV file
def write_to_csv(data, csv_path):
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['signature', 'body', 'docstring', 'id']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for entry in data:
            writer.writerow(entry)

# Collect all function data from kotlin files
all_functions_data = []
for root, dirs, files in os.walk(source_directory):
    for file in files:
        if file.endswith('.kt') or file.endswith('.kts'):
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")
            functions_data = extract_kotlin_functions(file_path)
            all_functions_data.extend(functions_data)
            print(f"Found {len(functions_data)} functions in {file_path}")
            print(f"Total functions found: {len(all_functions_data)}")
        if len(all_functions_data) >= 10000:
            break

# Write collected data to CSV
write_to_csv(all_functions_data, target_csv_path)

print(f"Dataset has been created at: {target_csv_path}")
