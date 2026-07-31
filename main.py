#!/usr/bin/env python
import datetime

import click

from Application import Application


def get_current_datetime():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d_%H_%M_%S")


def check_flag_callback(ctx, param, value):
    flag_name = f"{param.name}_exists"
    if value:
        ctx.params[flag_name] = True
    else:
        ctx.params[flag_name] = False
    return value


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--in_file",
    "-f",
    help="Input file path",
    required=True,
    type=click.Path(exists=True),
    prompt="Input path to the file to be anonymized",
)
@click.option(
    "--out_file",
    "-o",
    help="Output file path",
    required=False,
    type=click.Path(exists=False),
    default=f"{get_current_datetime()}.anonymized.txt",
    show_default=True,
)
@click.option(
    "--name_list",
    "-n",
    help="The path to the file containing the list of names to be anonymized",
    required=False,
    type=click.Path(exists=True, readable=True),
    callback=check_flag_callback,
    # prompt="Input the path to the list of names to be anonymized",
)
@click.option(
    "--id_list",
    "-i",
    help="The path to the file containing the list of IDs to be anonymized",
    required=False,
    type=click.Path(exists=True, readable=True),
    callback=check_flag_callback,
    # prompt="Input the path to the list of IDs to be anonymized",
)
@click.option(
    "--mapping",
    "-m",
    is_flag=True,
    default=False,
    help="Export anonymized mapping",
    show_default=True,
)
def anonymize(
    in_file, out_file, name_list, id_list, name_list_exists, id_list_exists, mapping
):
    app = Application(in_file, out_file, name_list, id_list)
    app.run_anonymization(
        anonymize_names=name_list_exists, anonymize_ids=id_list_exists, mapping=mapping
    )


if __name__ == "__main__":
    cli()
