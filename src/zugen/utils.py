import os 
from zugen import _shared_folder
import shutil
import toml
from zuu.app.pandoc import gen_file

def _check_path(path : str, token:str):
    """
    Check if the given path starts with the specified token and return the corresponding path in the shared folder.

    Args:
        path (str): The path to check.
        token (str): The token to search for in the path.

    Returns:
        str: The corresponding path in the shared folder, or None if the path does not start with the token.
    """
    if path.startswith(token):
        tlen = len(token)
        for o in os.listdir(_shared_folder):
            if os.path.exists(os.path.join(_shared_folder, o, path[tlen:])):
                return os.path.join(_shared_folder, o, path[tlen:])

def resolve_path(path : str):
    """
    Resolve the given path by checking if it exists in the shared folder or the current directory.

    Args:
        path (str): The path to resolve.

    Returns:
        str: The resolved path.

    Raises:
        FileNotFoundError: If the path does not exist.
    """
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
    """
    Perform standard Pandoc work, including generating a file, copying scripts, and capturing output.

    Args:
        data_path (str): The path to the data file.
        model_path (str): The path to the model file.
        template_path (str): The path to the template file.
        script_paths (list): A list of paths to script files.
        outtype (str): The output type.
        cwd (str): The current working directory.
    """
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
        print(f"Captured {captured}")
        shutil.copy(captured, curr_cwd)
    os.chdir(curr_cwd)

_captured = []

def capture(path :str):
    """
    Capture the specified path.

    Args:
        path (str): The path to capture.
    """
    _captured.append(path)

def ensure_file(path : str):
    """
    Ensure that the specified file exists and copy it to the current working directory.

    Args:
        path (str): The path to the file.
    """
    path = resolve_path(path)
    shutil.copy(path, os.getcwd())