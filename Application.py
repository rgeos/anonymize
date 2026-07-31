#!/usr/bin/env python

from FileHandler import FileHandler
from Change import ChangeName, ChangeID


class Application:
    def __init__(
        self, input_text_file, output_file, input_names_file=None, input_ids_file=None
    ):
        self.input_text_file = input_text_file
        self.output_file = output_file
        self.input_names_file = input_names_file
        self.input_ids_file = input_ids_file

        self.name_change = ChangeName()
        self.id_change = ChangeID()

    def run_anonymization(
        self, anonymize_names=True, anonymize_ids=False, mapping=False
    ):
        """
        Anonymizes names, IDs, or both depending on boolean flags passed.
        """
        # 1. Dynamically read lists only if their specific flag is toggled true
        names_to_replace = (
            FileHandler.read_lines(self.input_names_file)
            if (anonymize_names and self.input_names_file)
            else []
        )
        ids_to_replace = (
            FileHandler.read_lines(self.input_ids_file)
            if (anonymize_ids and self.input_ids_file)
            else []
        )

        text_lines = FileHandler.read_lines(self.input_text_file)
        modified_lines = []

        # 2. Iterate and process lines sequentially conditional on toggle choices
        for line in text_lines:
            modified_line = line

            if anonymize_names and names_to_replace:
                modified_line = self.name_change.get_real_name(
                    names_to_replace, modified_line
                )

            if anonymize_ids and ids_to_replace:
                modified_line = self.id_change.get_real_id(
                    ids_to_replace, modified_line
                )

            modified_lines.append(modified_line)

        # 3. Save finalized application content
        FileHandler.write_lines(self.output_file, modified_lines)
        print(f"Processed file saved to {self.output_file}")

        # 4. Generate mapping tables cleanly based on selections
        if mapping:
            if anonymize_names and names_to_replace:
                FileHandler.write_lines(
                    f"mapping_names_{self.output_file}",
                    self.name_change.mapping,
                    mapping=True,
                )
            if anonymize_ids and ids_to_replace:
                FileHandler.write_lines(
                    f"mapping_ids_{self.output_file}",
                    self.id_change.mapping,
                    mapping=True,
                )
            print("Mapping export steps processed.")

        print("Anonymization complete!")
