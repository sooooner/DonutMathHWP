import os
import json
import shutil


def get_basename(path):
    return os.path.basename(os.path.splitext(path)[0])

def list_all_files(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    
    return file_paths

def delect_all_files(directory):
    files = list_all_files(directory)
    for file_path in files:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            print(f"{file_path} 파일을 찾을 수 없습니다.")
        except PermissionError:
            print(f"{file_path} 파일을 삭제할 권한이 없습니다.")
        except Exception as e:
            print(f"파일 삭제 중 오류가 발생했습니다: {e}")
