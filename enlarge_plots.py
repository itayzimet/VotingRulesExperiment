import os

def insert_line_in_file(filepath, line_to_insert, line_number=3):
    # Read the content of the file
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Insert the new line at the specified line number (line_number - 1 for 0-based index)
    lines.insert(line_number - 1, line_to_insert + '\n')

    # Write the content back to the file
    with open(filepath, 'w') as file:
        file.writelines(lines)

def insert_line_in_multiple_files(directory, line_to_insert, extension=None):
    # Iterate over all the files in the given directory
    for filename in os.listdir(directory):
        # Skip if the item is not a file or doesn't have the specified extension (if provided)
        if not os.path.isfile(os.path.join(directory, filename)):
            continue
        if extension and not filename.endswith(extension):
            continue

        # Full path to the file
        filepath = os.path.join(directory, filename)

        # Insert line into the file
        insert_line_in_file(filepath, line_to_insert)

if __name__ == '__main__':
    # Specify the directory containing the files
    directory_path = r'C:\Users\Itayz\projects\alpha\Model1\images\tex'

    # The line you want to insert
    line_to_insert = r'\pgfplotsset{width=1\textwidth,height=0.7\textwidth}'

    # Optional: Specify file extension (e.g., '.txt' for text files)
    file_extension = '.tex'

    # Insert the line in all the files in the directory
    insert_line_in_multiple_files(directory_path, line_to_insert, file_extension)
