# Anonymize

Use [Faker library](https://faker.readthedocs.io/en/stable/index.html) to parse a text file and replace names and ID

## How to
1. create a text file with a list of names that need to be replaced (`name_list.txt`)
2. create a text file with a list of IDs that need to be replaced (`id_list.txt`)
3. assuming the file that needs names and/or IDs to be replaced is called `in_file.ext`, run the following command:
```bash
python main.py anonymize -f in_file.ext -nl name_list.txt -il id_list.txt
```

## Help menu
```text
python main.py anonymize --help
Usage: main.py anonymize [OPTIONS]

Options:
  -f, --in_file PATH        Input file path  [required]
  -o, --out_file PATH       Output file path  [default: 2026-08-04_10_32_47.anonymized.txt]
  -nl, --name_list PATH     The path to the file containing the list of names to be anonymized
  -il, --id_list PATH       The path to the file containing the list of IDs to be anonymized
  -dl, --disease_list PATH  The path to the file containing the list of diseases to be replaced
  -ln, --last_names PATH    The path to the file containing the list of last_names to be anonymized
  -fn, --first_names PATH   The path to the file containing the list of first_names to be anonymized
  -m, --mapping             Export anonymized mapping
  -l, --locale TEXT         The locale to use  [default: ja_JP]
  --help                    Show this message and exit.
```

