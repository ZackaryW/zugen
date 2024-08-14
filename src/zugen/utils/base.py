import os
from zugen import _shared_folder

def resolve_path(path : str):
    _m = {
        7 : "shared/",
        2 : "~/"
    }
    for k, v in _m.items():
        if path.startswith(v):
            for o in os.listdir(_shared_folder):
                if os.path.exists(os.path.join(_shared_folder, o, path[k:])):
                    return os.path.join(_shared_folder, o, path[k:])
            
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    
    return path

