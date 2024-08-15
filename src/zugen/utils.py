import os 
from zugen import _shared_folder
import shutil
import toml
from zuu.app.pandoc import gen_file


def _check_path(path : str, token:str):
    if path.startswith(token):
        tlen = len(token)
        for o in os.listdir(_shared_folder):
            if os.path.exists(os.path.join(_shared_folder, o, path[tlen:])):
                return os.path.join(_shared_folder, o, path[tlen:])

def resolve_path(path : str):

    if (p:= _check_path(path, "shared/")):
        return p
    elif (p:= _check_path(path, "@/")):
        return p
            
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    
    return path


def std_pandoc_work(data_path,
    model_path : str,
    template_path : str,
    script_paths : list,
    outtype : str,
    cwd : str
):
    curr_cwd = os.getcwd()
    os.chdir(cwd)

    if model_path:
        # TODO
        pass

    data = toml.load(data_path)

    gen_file(os.getcwd(), outtype, template_path, data)

    for script_path in script_paths:
        script_path : str
        shutil.copy(script_path, os.getcwd())
        if script_path.endswith(".py"):
            with open(script_path, "r") as f:
                exec(f.read(), globals())
        elif script_path.endswith(".ps1"):
            os.system("powershell -File %s" % script_path)
        elif script_path.endswith(".bat"):
            os.system("cmd /c %s" % script_path)
        else:
            raise NotImplementedError(script_path)

    for captured in _captured:
        shutil.copy(captured, os.getcwd())
    os.chdir(curr_cwd)

_captured = []

def capture(path :str):
    _captured.append(path)

def ensure_file(path : str):
    path = resolve_path(path)
    shutil.copy(path, os.getcwd())