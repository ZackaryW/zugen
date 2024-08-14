
import os as _os
from zuu.app.scoop import is_scoop_installed as _is_scoop_installed
from zuu.stdpkg.subprocess import check_is_installed as _check_is_installed
from zuu.struct.simple_io_dict import SimpleIODict as _SimpleIODict
import time as _time
import logging as _logging


#ANCHOR check install
if not _is_scoop_installed():
    print("scoop is not installed")
    exit(1)

_pandoc_installed = _check_is_installed("pandoc")
_zugen_no_install =  "ZUGEN_NO_INSTALL" in _os.environ
    
if not _pandoc_installed and not _zugen_no_install:
    print("pandoc is not installed")
    exit(1)

if not _pandoc_installed:
    _os.system("scoop update")
    _os.system("scoop install git")
    _os.system("scoop bucket add extras")
    _os.system("scoop install pandoc")

#ANCHOR check config
# create a .zugen/shared folder at public home
_zugen_folder = _os.path.join(_os.path.expanduser("~"), ".zugen")
_shared_folder = _os.path.join(_zugen_folder, "shared")
_os.makedirs(_shared_folder, exist_ok=True)

_zugen_config_path = _os.path.join(_zugen_folder, "config.json")
zugen_config = _SimpleIODict(_zugen_config_path, {"buckets" : [
    ["https://github.com/ZackaryW/zugen.git", "resources"]
]})


def _update_buckets(config, ignore_last_checked=False):
    if _time.time() - config.get("last_checked", 0) <= 24 * 60 * 60 and not ignore_last_checked:
        return False
    config["last_checked"] = _time.time()
    _curr_cd = _os.getcwd()
    _os.chdir(_shared_folder)
    for i, bucket in enumerate(config["buckets"]):
        url = bucket[0] if isinstance(bucket, list) else bucket
        branch = bucket[1] if isinstance(bucket, list) else "main"
        print("updating %s" % url)
        _os.makedirs(f"{i}", exist_ok=True)
        _os.chdir(f"{i}")
        if not _os.path.exists(".git"):
            _os.system("git init")
            _os.system(f"git remote add origin {url}")
            _os.system(f"git fetch origin {branch}")
            _os.system(f"git checkout {branch}")

        _os.system("git pull")
        _os.chdir(_shared_folder)
    _os.chdir(_curr_cd)     
    _logging.info("no need to update shared resources")

if _os.environ.get("ZU_NO_UPDATE", False):
    _logging.info("no need to update shared resources")
else:
    _update_buckets(zugen_config)

