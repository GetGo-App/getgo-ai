import json

def load_file_text(path):
    with open(path, 'r') as f:
        return f.read()

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)
    
def save_json(path, file_save):
    with open(path, 'w') as f:
        return json.dump(file_save, f, ensure_ascii=False)
    
def get_data(paths):
    data = {}
    for key, path in paths.items():
        data[key] = load_file_text(path)
    return data
