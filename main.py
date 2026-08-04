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
    "-nl",
    help="The path to the file containing the list of names to be anonymized",
    required=False,
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "--id_list",
    "-il",
    help="The path to the file containing the list of IDs to be anonymized",
    required=False,
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "--disease_list",
    "-dl",
    help="The path to the file containing the list of diseases to be replaced",
    required=False,
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "--last_names",
    "-ln",
    help="The path to the file containing the list of last_names to be anonymized",
    required=False,
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "--first_names",
    "-fn",
    help="The path to the file containing the list of first_names to be anonymized",
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "--mapping",
    "-m",
    is_flag=True,
    default=False,
    help="Export anonymized mapping",
    show_default=True,
)
@click.option(
    "--locale",
    "-l",
    default="ja_JP",
    help="The locale to use",
    show_default=True,
)
def anonymize(
    in_file,
    out_file,
    name_list,
    id_list,
    disease_list,
    mapping,
    locale,
    last_names,
    first_names,
):
    app = Application(
        locale=locale, last_name_path=last_names, first_name_path=first_names
    )
    app.register_task(name_list, "get_name_strategy", "NAMES")
    app.register_task(id_list, "get_uuid_strategy", "IDS")
    app.register_task(disease_list, "get_disease_strategy", "DISEASE")

    app.run_anonymization(in_file, out_file, mapping)


if __name__ == "__main__":
    cli()
