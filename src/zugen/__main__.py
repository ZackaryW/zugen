import os
import sys
sys.path.append(os.path.dirname(__file__))
import shutil
import tempfile
import click
from zuu.stdpkg.logging import basic_debug

from zugen import scriptUtils

from zugen.utils import resolve_path

from zugen.core import read_profile, standard_zugen_workflow

from zuu.usrapp.gh_repo_cache import click_add_command

@click.group(invoke_without_command=True)
@click.option("--debug", "-d", is_flag=True, help="debug mode")
#@click.option("--scoop", "-s", is_flag=True, help="scoop environment")
@click.pass_context
def cli(ctx : click.Context, debug):
    if debug:
        basic_debug()

    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())

@cli.group("cacher")
def cacher():
    pass

click_add_command(cacher)

@cli.command("gen")
@click.option("--profile", "-p", help="profile to use")
#
@click.option("--template", "-t", help="template to use")
@click.option("--script", "-s", help="script to use")
@click.option("--data", "-d", help="data to use")
# @click.option("--model", "-m", help="model to use")
#
@click.option("--use-cacher", "-uc", is_flag=True, help="use cacher to resolve paths")
#
@click.option("--temp", "-t", help="designate temp folder")
@click.option("--verbose", "-v", is_flag=True, help="verbose mode")
@click.option("--outname", "-on", help="output name, only useful if no script defined")
@click.option("--outpath", "-o", help="output path, only useful if no script defined")
def _gen(**kwargs):
    profile = kwargs.get("profile", None)

    template = kwargs.get("template", None)
    script = kwargs.get("script", None)
    data = kwargs.get("data", None)

    use_cacher = kwargs.get("use_cacher", False)
    temp = kwargs.get("temp", False)

    verbose = kwargs.get("verbose", False)

    outname = kwargs.get("outname", None)

    outpath = kwargs.get("outpath", None)

    if not any([profile, template, script, data]):
        click.echo("no profile, template, script, or data specified")
        return

    if profile:
        try:
            data_path, script_path, template_path = read_profile(profile, use_cacher)
        except FileNotFoundError:
            click.echo("profile not found")
            return

    if template:
        template_path = resolve_path(template, use_cacher)
        if not template_path:
            click.echo("template not found")
            return

    if script:
        script_path = resolve_path(script, use_cacher)
        if not script_path:
            click.echo("script not found")
            return

    if data:
        data_path = resolve_path(data, use_cacher)
        if not data_path:
            click.echo("data not found")
            return

    # if not cases
    if not data_path and os.path.exists("data.toml"):
        data_path = os.path.abspath("data.toml")

    if not template_path:
        for f in os.listdir(os.getcwd()):
            if f.endswith(".template"):
                template_path = os.path.abspath(f)
                break

    if not data_path or not template_path:
        click.echo("template or data not found")
        return

    if not temp:
        tempdirobj = tempfile.TemporaryDirectory()
        tempdir = tempdirobj.name
    else:
        os.makedirs(temp, exist_ok=True)
        tempdir = os.path.abspath(temp)


    curr_cwd = os.path.abspath(os.getcwd())
    success = False
    try:
        e= None
        os.chdir(tempdir)
        success = standard_zugen_workflow(
            workpath = tempdir,
            data_path = data_path,
            template_path = template_path,
            script_path = script_path,
            outname = outname,
            verbose = verbose,
            allow_unsafe = False
        )

        if outpath:
            os.makedirs(outpath, exist_ok=True)

    except Exception as e:
        click.echo(e)
    finally:
        os.chdir(curr_cwd)
        if success or verbose:
            target_list = os.listdir(tempdir) if not success else scriptUtils.captureList
            for file in target_list:
                click.echo(f"grabbing {file}")
                if outpath:
                    shutil.move(os.path.join(tempdir, file), os.path.join(outpath, file))
                elif e:
                    os.makedirs("debug", exist_ok=True)
                    shutil.move(os.path.join(tempdir, file), os.path.join(curr_cwd, "debug", file))
                else:
                    shutil.move(os.path.join(tempdir, file), os.path.join(curr_cwd, file))
        
        if not temp:
            tempdirobj.cleanup()

if __name__ == "__main__":
    cli()