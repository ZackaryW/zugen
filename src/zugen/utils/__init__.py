import os as _os
from zugen import _shared_folder

def resolve_path(path : str):
    _m = {
        7 : "shared/",
        2 : "~/"
    }
    for k, v in _m.items():
        if path.startswith(v):
            for o in _os.listdir(_shared_folder):
                if _os.path.exists(_os.path.join(_shared_folder, o, path[k:])):
                    return _os.path.join(_shared_folder, o, path[k:])
            
    if not _os.path.exists(path):
        raise FileNotFoundError(path)
    
    return path

