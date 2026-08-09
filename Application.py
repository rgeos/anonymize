#!/usr/bin/env python

import logging
import re
import os
import sys
from FileHandler import FileHandler
from multiprocessing import Pool, cpu_count
from Anonymizer import (
    Anonymizer,
    init_worker,
    worker_process_chunk,
)


class Application:
    def __init__(self, locale="ja_JP", last_name_path=None, first_name_path=None):
        self.tasks = []
        self.master_engines = {}
        self.locale = locale
        self.strategy_provider = Anonymizer(
            locale=locale,
            last_name_path=last_name_path,
            first_name_path=first_name_path,
        )

    def _make_non_greedy(self, pattern_str):
        """
        Converts greedy quantifiers (*, +, ?, {m,n}) to non-greedy (*?, +?, ??, {m,n}?)
        safely checking that they aren't already followed by a '?' or modified inside groups.
        """
        # Improved pattern to accurately match only greedy quantifiers
        # while respecting existing '?' operators.
        greedy_quantifier_pattern = re.compile(r"(\*|\+|\?|\{\d*,?\d*\})(?!\?)")
        non_greedy_version = greedy_quantifier_pattern.sub(r"\1?", pattern_str)

        # If the user already provided a perfect non-greedy pattern, we leave it alone
        if non_greedy_version != pattern_str:
            logging.info(
                f"Converted greedy pattern to non-greedy: '{non_greedy_version}'"
            )
        return pattern_str if ".*?" in pattern_str else non_greedy_version

    def register_task(self, file_or_pattern, strategy_name, prefix):
        """Accepts file path or regex pattern."""
        self.tasks.append((file_or_pattern, strategy_name, prefix))

    def run_anonymization(
        self, input_text_file, output_text_file, mapping=False, chunk_size=100000
    ):
        """Runs optimization pipeline using deterministic master maps and chunks."""
        logging.info(
            "1. Building static master dictionary translations mapping indexes..."
        )

        input_text_content = None

        for file_or_pattern, strategy_name, prefix in self.tasks:
            if not file_or_pattern:
                continue

            # Check if input is a valid existing file path
            if os.path.exists(str(file_or_pattern)):
                terms = FileHandler.read_file(file_or_pattern)
            else:
                # enforce non-greedy behavior
                logging.info(
                    f"2. Pattern file not found for {prefix}. Treating input as regex."
                )
                processed_pattern = self._make_non_greedy(str(file_or_pattern))

                if input_text_content is None:
                    with open(
                        input_text_file, "r", encoding="utf-8", errors="replace"
                    ) as f:
                        input_text_content = f.read()

                try:
                    compiled = re.compile(processed_pattern)
                    raw_matches = compiled.findall(input_text_content)

                    terms = []
                    for match in raw_matches:
                        if isinstance(match, tuple):
                            # If multiple capture groups exist, use the full match string if possible,
                            # or join groups together.
                            terms.append("".join(match))
                        else:
                            terms.append(match)

                except re.error as e:
                    logging.critical(
                        f"FATAL: Malformed regex pattern syntax for {prefix} -> '{file_or_pattern}'"
                    )
                    raise ValueError(f"Invalid regex syntax: {e}") from e

            if not terms:
                continue

            strategy_method = getattr(self.strategy_provider, strategy_name)()

            mapping_dict = {}
            for term in sorted(set(terms)):
                if term:
                    mapping_dict[term] = strategy_method()

            self.master_engines[prefix] = mapping_dict

        num_cores = max(1, cpu_count() - 1)
        logging.info(
            f"3. Distributing process pipelines workloads over {num_cores} cores ..."
        )

        with Pool(
            processes=num_cores,
            initializer=init_worker,
            initargs=(self.master_engines,),
        ) as pool:
            chunks = FileHandler.read_lines(input_text_file, chunk_size=chunk_size)
            results = pool.imap(worker_process_chunk, chunks)

            logging.info(
                f"4. Streaming outputs onto disk output target: {output_text_file}"
            )
            with open(output_text_file, "w", encoding="utf-8") as out_f:
                for processed_chunk in results:
                    out_f.writelines(processed_chunk)

        logging.info("5. Pipeline executed successfully.")

        if mapping:
            logging.info(f"6. Writing mapping file")
            for prefix, engine in self.master_engines.items():
                FileHandler.write_file(f"mapping_{prefix}_{output_text_file}", engine)

        logging.info("7. Anonymization completed.")
