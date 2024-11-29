import os

def create_file_force(self, filepath: str) -> None:
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('')
        except PermissionError:
            print(f"Permission denied. Cannot create file {filepath}. Please, check permissions.")
            exit(1)
        except Exception as e:
            print(f"Error while creating file {filepath}. The actual exception was:\n {e}")
            exit(1)

def file_exists(filepath: str) -> bool:
    return os.path.exists(filepath)