import shutil
import typing
import os
import click
import toml
from zuu.app.pandoc import gen_file

from .utils import resolve_path, resolve_template_type

workDirectory: str = None
captureList: typing.List[str] = []
inputData : dict = None
templatePath : str = None
outNameOverride : str = None

def set_data(obj: typing.Union[str, dict]):
    global inputData
    if isinstance(obj, str):
        inputData = toml.load(obj)
    else:
        assert isinstance(obj, dict)
        inputData = obj

def default_data(obj : typing.Union[str, dict]):
    if inputData:
        return
    set_data(obj)


def ensure_file(path: str):
    apath = resolve_path(path, True)
    if not path:
        raise FileNotFoundError(f"file not found: {path}")

    shutil.copy(apath, os.path.basename(path))



def pandoc():
    assert inputData

    template_type = resolve_template_type(templatePath)

    gen_file(
        workDirectory,
        template_type,
        templatePath,
        inputData,
        outNameOverride if outNameOverride else "pandoc.out",
    )


def rename(path1: str, path2: str):
    try:
        os.rename(path1, path2)
    except Exception as e:
        raise e


def system(command: str, throw : bool = True):
    res = os.system(command)
    if res != 0 and throw:
        raise click.ClickException(
            f"An error occurred while running the command: {command}"
        )


def capture(path: str):
    global captureList
    if path not in os.listdir():
        raise ValueError("must be current cwd files")

    if os.path.exists(path) and path not in captureList:
        captureList.append(path)