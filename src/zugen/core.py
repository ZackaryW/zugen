import os
import shutil

import toml
from .utils import resolve_path
import zugen.scriptUtils as scriptUtils

methods = {
    "default_data": scriptUtils.default_data,
    "ensure_file": scriptUtils.ensure_file,
    "pandoc": scriptUtils.pandoc,
    "rename": scriptUtils.rename,
    "system": scriptUtils.system,
    "capture" : scriptUtils.capture,
    "__base__" : scriptUtils,
}

def read_profile(path: str, useCacher: bool = False):
    profile_path = resolve_path(path, useCacher=useCacher)
    if not profile_path:
        raise FileNotFoundError(f"profile not found: {path}")

    data_path = script_path = template_path = None

    if os.path.exists(os.path.join(profile_path, "data.toml")):
        data_path = os.path.join(profile_path, "data.toml")

    if os.path.exists(os.path.join(profile_path, "script.py")):
        script_path = os.path.join(profile_path, "script.py")

    for file in os.listdir(profile_path):
        if file.startswith("template."):
            template_path = os.path.join(profile_path, file)
            break

    return data_path, script_path, template_path


def create_default_script(template_path: str):
    template_extension = os.path.splitext(template_path)[1]


    return f"""
    __base__.outNameOverride = "output.{template_extension}"
    pandoc()
    """

def standard_zugen_workflow(
    workpath: str,
    data_path: str = None,
    template_path: str = None,
    script_path: str = None,
    outname: str = None,
    verbose : bool = False,
    allow_unsafe : bool = False
):
    scriptUtils.workDirectory = workpath
    scriptUtils.outNameOverride = outname

    if verbose and data_path:
        shutil.copy(data_path, "data.toml")
    
    if data_path:
        data = toml.load(data_path)
        scriptUtils.inputData = data

    if verbose and template_path:
        shutil.copy(template_path, os.path.basename(template_path))
        scriptUtils.templatePath = os.path.basename(template_path)
    elif template_path:
        scriptUtils.templatePath = template_path

    if verbose and script_path:
        shutil.copy(script_path, os.path.basename(script_path))
    
    if script_path:
        with open(script_path, "r") as f:
            script_content = f.read()
    else:
        script_content = create_default_script(template_path)
    
    if not allow_unsafe and "import" in script_content:
        raise RuntimeError("Unsafe script detected. Use --allow-unsafe to run.")

    global_vars = {}
    global_vars.update(methods)
    exec(script_content, global_vars)
    return True



    
