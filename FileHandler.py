#!/usr/bin/env python


class FileHandler:
    """
    Reading the file
    """

    @staticmethod
    def read_lines(file_path):
        """
        Reading the file line by line
        """
        with open(file_path, "r") as f:
            return [line.rstrip("\n") for line in f.readlines()]

    @staticmethod
    def write_lines(file_path, lines, mapping=False):
        with open(file_path, "w") as f:
            if mapping:
                for original_name, fake_name in lines.items():
                    f.write(f"{original_name} -> {fake_name}\n")
            else:
                for line in lines:
                    f.write(f"{line}\n")
