#!/usr/bin/env python

import logging
import json
from FileHandler import FileHandler
from multiprocessing import Pool, cpu_count
from Anonymizer import (
    Anonymizer,
    init_worker,
    worker_process_chunk,
)


class Application:
    def __init__(self):
        self.tasks = []
        self.master_engines = {}
        self.strategy_provider = Anonymizer()

    def register_task(self, file_path, strategy_name, prefix):
        """Queues targeted mask execution instructions profiles."""
        self.tasks.append((file_path, strategy_name, prefix))

    def run_anonymization(
        self, input_text_file, output_text_file, mapping=False, chunk_size=100000
    ):
        """Runs optimization pipeline using deterministic master maps and chunks."""
        logging.info(
            "1. Building static master dictionary translations mapping indexes..."
        )
        for file_path, strategy_name, prefix in self.tasks:
            terms = FileHandler.read_file(file_path)
            if not terms:
                continue

            strategy_method = getattr(self.strategy_provider, strategy_name)()

            mapping_dict = {}
            for term in sorted(set(terms)):
                mapping_dict[term] = strategy_method()

            self.master_engines[prefix] = mapping_dict

        num_cores = max(1, cpu_count() - 1)
        logging.info(
            f"2. Distributing process pipelines workloads over {num_cores} cores ..."
        )

        with Pool(
            processes=num_cores,
            initializer=init_worker,
            initargs=(self.master_engines,),
        ) as pool:
            chunks = FileHandler.read_lines(input_text_file, chunk_size=chunk_size)

            results = pool.imap(worker_process_chunk, chunks)

            logging.info(
                f"3. Streaming outputs onto disk output target: {output_text_file}"
            )
            with open(output_text_file, "w", encoding="utf-8") as out_f:
                for processed_chunk in results:
                    out_f.writelines(processed_chunk)

        logging.info("4. Pipeline executed successfully.")

        if mapping:
            logging.info(f"5. Writing mapping file")
            for prefix, engine in self.master_engines.items():
                FileHandler.write_file(f"mapping_{prefix}_{output_text_file}", engine)

        logging.info("6. Anonymization completed.")
