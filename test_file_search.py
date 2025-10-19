import os
from collections import defaultdict
from datetime import datetime

# First, let's create some test files to demonstrate the functionality
test_files = ['example.txt', 'test.py', 'data.csv', 'document.docx']

# Create test files if they don't exist
for filename in test_files:
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write(f"This is a test file: {filename}\n")
            f.write(f"Created for demonstration purposes.\n")
        print(f"Created test file: {filename}")

# File search and directory implementation
file_list = ['example.txt', 'test.py', 'data.csv', 'document.docx', 'image.jpg', 'nonexistent.txt']
search_file = 'test.py'
file_directory = defaultdict(dict)

print("\n=== File Search and Directory System ===")
print(f"Searching for files in: {os.getcwd()}")
print("\nProcessing file list...")

# Process each file in the list
for filename in file_list:
    if os.path.exists(filename):
        try:
            file_stats = os.stat(filename)
            file_directory[filename] = {
                'size': file_stats.st_size,
                'created': datetime.fromtimestamp(file_stats.st_ctime),
                'modified': datetime.fromtimestamp(file_stats.st_mtime),
                'path': os.path.abspath(filename),
                'exists': True
            }
            print(f"✓ Found and indexed: {filename}")
        except Exception as e:
            print(f"✗ Error processing {filename}: {e}")
    else:
        print(f"✗ File not found: {filename}")

print(f"\n=== Search Results ===")
print(f"Looking for file: {search_file}")

# Search for the specific file
if search_file in file_directory:
    file_details = file_directory[search_file]
    print(f"\n🎉 File found: {search_file}")
    print(f"   Size: {file_details['size']} bytes")
    print(f"   Created: {file_details['created']}")
    print(f"   Modified: {file_details['modified']}")
    print(f"   Full Path: {file_details['path']}")
else:
    print(f"\n❌ File '{search_file}' not found in the system")

# Display all valid files in directory
print(f"\n=== File Directory Summary ===")
print(f"Total valid files found: {len(file_directory)}")

if file_directory:
    print("\nAll indexed files:")
    for filename, details in file_directory.items():
        print(f"  • {filename} ({details['size']} bytes)")
else:
    print("No valid files found in the directory.")

# Demonstrate file retrieval functionality
print(f"\n=== File Details Retrieval Demo ===")
user_file = input("Enter a filename to get details (or press Enter to skip): ").strip()

if user_file:
    if user_file in file_directory:
        details = file_directory[user_file]
        print(f"\nDetails for '{user_file}':")
        print(f"  Size: {details['size']} bytes")
        print(f"  Created: {details['created']}")
        print(f"  Modified: {details['modified']}")
        print(f"  Path: {details['path']}")
    else:
        print(f"\nFile '{user_file}' not found in directory.")
        if os.path.exists(user_file):
            print("(File exists but wasn't in our original search list)")
else:
    print("No filename entered, skipping retrieval demo.")

print("\nProgram completed successfully!")
