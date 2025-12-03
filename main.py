#!/usr/bin/env python
import datetime

import click

from Application import Application


def get_current_datetime():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d_%H_%M_%S")


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--name_list",
    "-l",
    help="The path to the file containing the list of names to be anonymized",
    required=True,
    type=click.Path(exists=True),
    prompt="Input the path to the list of names to be anonymized",
)
@click.option(
    "--in_file",
    "-i",
    help="Input file path",
    required=True,
    type=click.Path(exists=True),
    prompt="Input path to the file that needs to be anonymized",
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
    "--mapping",
    "-m",
    is_flag=True,
    default=False,
    help="Export anonymized mapping",
    show_default=True,
)
def anonymize(name_list, in_file, out_file, mapping):
    app = Application(name_list, in_file, out_file)
    app.run_anonymization(mapping=mapping)


if __name__ == "__main__":
    cli()
