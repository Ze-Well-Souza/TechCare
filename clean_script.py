import sys

file_path = sys.argv[1]

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

cleaned_content = content.replace('obe', '')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(cleaned_content)

print(f'File {file_path} cleaned.')
