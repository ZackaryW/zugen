import os
import tempfile
import click
from zugen import zugen_config, _update_buckets, _zugen_folder
from zugen.utils import resolve_path, std_pandoc_work
import toml

@click.group()
def cli():
    pass

@cli.group("config")
def config():
    pass

@config.command("folder")
def config_folder():
    os.startfile(_zugen_folder)

@cli.group("bucket")
def bucket():
    pass

@bucket.command("add")
@click.argument("url")
@click.option("--branch", "-b")
def add_bucket(url, branch):
    if branch:
        zugen_config["buckets"].append([url, branch]) 
    else:
        zugen_config["buckets"].append(url)

    zugen_config._save()
    click.echo(f"added bucket {url}")

@bucket.command("list")
def list_bucket():
    if not zugen_config["buckets"]:
        click.echo("No buckets found.")
    else:
        for index, bucket in enumerate(zugen_config["buckets"]):
            if isinstance(bucket, list):
                click.echo(f"{index}. {bucket[0]} (branch: {bucket[1]})")
            else:
                click.echo(f"{index}. {bucket}")

@bucket.command("remove")
@click.argument("index")
def remove_bucket(index):
    index = int(index)
    if index >= len(zugen_config["buckets"]):
        click.echo(f"index {index} out of range")

    zugen_config["buckets"].pop(index)
    zugen_config._save()
    click.echo(f"removed bucket {index}")

@bucket.command("update")
@click.option("--ignore-last-checked", "-i", is_flag=True)
def update_buckets(ignore_last_checked):
    res = _update_buckets(zugen_config, ignore_last_checked)
    if res is False:
        click.echo("last checked less than 24 hours ago, skipping")


@cli.command("gen")
@click.argument("data", default="data.toml")
@click.option("--profile", "-p", help="profile name")
@click.option("--template", "-t", help="template name")
@click.option("--model", "-m", help="model name")
# allow multiple scripts
@click.option("--script", "-s", help="script name", multiple=True)
@click.option("--outtype", "-o", help="output type")
@click.option("--no-temp", "-n", is_flag=True, help="don't use temp folder")
def gen_cmd(data, profile : str, template:str, model : str, script : list, outtype : str, no_temp : bool = False):    

    need_profile = not template and not model and not script and not outtype
    if need_profile and not profile:
        click.echo("profile name required")
        return
    
    try:
        if need_profile:
            if profile.startswith("@") or profile.startswith("shared"):
                profile = resolve_path(profile)
                with open(profile, "r") as f:
                    profiledict = toml.load(f)
            else:
                profiledict = zugen_config.get("profile", {}).get(profile, {})
            template = profiledict.get("template", None)
            model = profiledict.get("model", None)
            script = profiledict.get("script", [])
            outtype = profiledict.get("outtype", None)
            internaldata = profiledict.get("internaldata", None)
            if internaldata is not None:
                data = internaldata

        template_path = resolve_path(template)
        if model:
            model_path = resolve_path(model)
        else:
            model_path = None
            
        script_paths = [resolve_path(s) for s in script]

    except FileNotFoundError as e:
        click.echo(f"file not found: {e}")
        return

    try:
        tempdir = tempfile.TemporaryDirectory() if not no_temp else None
        cwd = os.getcwd() if no_temp else tempdir.name

        std_pandoc_work(
            data_path=resolve_path(data),
            model_path=model_path,
            template_path=template_path,
            script_paths=script_paths,
            outtype=outtype,
            cwd=cwd
        )

    except Exception as e:
        click.echo(f"error: {e}")
    finally:
        if tempdir:
            tempdir.cleanup()

    if not need_profile and profile:
        click.echo(f"saving profile {profile}")
        zugen_config.setdefault("profile", {})[profile] = {
            "template": template,
            "model": model,
            "script": script,
            "outtype": outtype
        }   
        zugen_config._save()

if __name__ == "__main__":
    cli()