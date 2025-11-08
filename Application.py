#!/usr/bin/env python

from FileHandler import FileHandler
from NameChange import NameChange


class Application:
    def __init__(
        self, input_strings_file, input_text_file, output_file, locale="ja_JP"
    ):
        self.input_strings_file = input_strings_file
        self.input_text_file = input_text_file
        self.output_file = output_file
        self.locale = locale
        self.name_change = NameChange(locale)

    def run_anonymization(self, mapping=False):
        """
        Anonymize the list of names in the input file
        """
        strings_to_replace = FileHandler.read_lines(self.input_strings_file)
        text_lines = FileHandler.read_lines(self.input_text_file)
        modified_lines = []

        for line in text_lines:
            modified_line = self.name_change.get_real_name(strings_to_replace, line)
            modified_lines.append(modified_line)

        FileHandler.write_lines(self.output_file, modified_lines)
        print(f"Processed file saved to {self.output_file}")

        # if you need the mapping between the real <> fake name
        if mapping:
            FileHandler.write_lines(
                f"mapping_{self.output_file}",
                self.name_change.name_mapping,
                mapping=True,
            )
            print(f"Mapping file saved to mapping_{self.output_file}")

        print("Anonymization complete!")
