#!/usr/bin/env python
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


class FileHandler:
    """
    Reading the file
    """

    @staticmethod
    def read_lines(file_path, chunk_size=10000):
        chunk = []
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                chunk.append(line)
                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []
            if chunk:
                yield chunk

    @staticmethod
    def write_lines(file_path, lines, mapping=False):
        with open(file_path, "w") as f:
            if mapping:
                for original_name, fake_name in lines.items():
                    f.write(f"{original_name} -> {fake_name}\n")
            else:
                for line in lines:
                    f.write(f"{line}\n")

    @staticmethod
    def read_file(file_path):
        if not file_path or not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return []
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return [line.rstrip("\n") for line in f.readlines()]

    @staticmethod
    def write_file(file_path, mapping_dict):
        """Helper to write original -> fake mapping files out to disk."""
        with open(file_path, "w", encoding="utf-8") as f:
            for original_value, fake_value in mapping_dict.items():
                f.write(f"{original_value} -> {fake_value}\n")
