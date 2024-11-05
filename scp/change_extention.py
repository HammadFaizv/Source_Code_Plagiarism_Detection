import os

def change_extension_to_java(directory_path):
    """Changes the extension of all files in the given directory to .java."""
    for filename in os.listdir(directory_path):
        # Split the file into name and extension
        name, ext = os.path.splitext(filename)
        
        # Skip files that already have the .java extension
        if ext != ".java":
            # Define the new filename with .java extension
            new_filename = f"{name}.java"
            
            # Get full paths
            old_file = os.path.join(directory_path, filename)
            new_file = os.path.join(directory_path, new_filename)
            
            # Rename the file
            os.rename(old_file, new_file)
            print(f"Renamed: {filename} -> {new_filename}")

# Usage
if __name__ == "__main__":
    # run if not
    directory_path = "./scp/data"
    change_extension_to_java(directory_path)