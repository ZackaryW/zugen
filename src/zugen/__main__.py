import os
import click
from zugen import zugen_config, _update_buckets, _zugen_folder

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


if __name__ == "__main__":
    cli()