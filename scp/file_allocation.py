import shutil
import os

def move_file(source_path, destination_path):
    if os.path.isfile(source_path):
        try:
            shutil.copy(source_path, destination_path)
            print(f"File moved from {source_path} to {destination_path} successfully.")
        except PermissionError:
            print("Permission denied. Please check your access rights.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("The specified file does not exist or is not a regular file.")

def create_file_list(list_path, file_path, destination_path):
    files = []
    counter = 0
    with open(list_path, "r") as file_list:
        while True:
            line = file_list.readline()
            if not line:
                break
            line = line.strip()
            for code_file in line.split(' '):
                if code_file not in files:
                    dir_path = os.path.join(file_path, code_file[:2], code_file)
                    move_file(dir_path, destination_path)
                    files.append(code_file)
                    counter += 1
    print(f"{counter} files have been moved.")
    return files

def move_more_files(file_path, destination_path, files_list):
    counter = 0
    files = os.listdir(file_path+"/A1")
    files = files[:300]
    for file in files:
        if file not in files_list:
            dir_path = os.path.join(file_path, "A1", file)
            move_file(dir_path, destination_path)
            counter += 1
            # return None
    print(f"{counter} more files have been moved.")

if __name__ == "__main__":
    list_path = "../soco14_test_dataset/soco14_java_list.qrel"
    file_path = "../soco14_test_dataset/java"
    destination_path = "./scp/data"
    files = create_file_list(list_path, file_path, destination_path)
    move_more_files(file_path, destination_path, files)