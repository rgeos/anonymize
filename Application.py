#!/usr/bin/env python

import os
from FileHandler import FileHandler
from multiprocessing import Pool
from Anonymizer import Anonymizer, AnonymizationStrategies

anonymizer_registry = []


def init_worker(configs):
    """
    configs: A list of tuples containing (target_terms_list, strategy_name)
    """
    global anonymizer_registry
    anonymizer_registry = []

    strategies = AnonymizationStrategies()

    for terms, strategy_name in configs:
        if terms and hasattr(strategies, strategy_name):
            strategy_func = getattr(strategies, strategy_name)()
            engine = Anonymizer(terms, strategy_func)
            anonymizer_registry.append(engine)


def worker_process_chunk(chunk_lines):
    processed_lines = []
    for line in chunk_lines:
        modified_line = line
        # Pipe the line through every active anonymizer engine sequentially
        for anonymizer in anonymizer_registry:
            modified_line = anonymizer.process_line(modified_line)
        processed_lines.append(modified_line)
    return processed_lines


class Application:
    def __init__(self, input_text_file, output_file):
        self.input_text_file = input_text_file
        self.output_file = output_file
        self.tasks = []

    def add_anonymization_task(self, target_file_path, strategy_name, mapping_prefix):
        self.tasks.append((target_file_path, strategy_name, mapping_prefix))

    def run_anonymization(self, mapping=False, chunk_size=10000):
        print("Step 1: Parsing lookup layers and pre-building translation maps...")
        worker_configs = []
        master_engines = {}
        strategies = AnonymizationStrategies()

        for file_path, strategy_name, prefix in self.tasks:
            terms = FileHandler.read_file(file_path)
            if terms:
                worker_configs.append((terms, strategy_name))
                strategy_func = getattr(strategies, strategy_name)()
                master_engines[prefix] = Anonymizer(terms, strategy_func)

        print("Step 2: Loading source text structure...")
        text_lines = FileHandler.read_file(self.input_text_file)
        chunks = [
            text_lines[i : i + chunk_size]
            for i in range(0, len(text_lines), chunk_size)
        ]

        print("Step 3: Launching parallel multi-core engine pools...")
        num_cores = os.cpu_count() or 4

        with Pool(
            processes=num_cores, initializer=init_worker, initargs=(worker_configs,)
        ) as pool:
            print("Step 4: Executing map-reduce processing across workers...")
            chunk_results = pool.map(worker_process_chunk, chunks)

        print("Step 5: Saving main anonymized output file...")
        all_lines = [line for chunk in chunk_results for line in chunk]
        FileHandler.write_lines(self.output_file, all_lines)

        if mapping:
            print("Step 6: Exporting matching translation matrices...")
            for prefix, engine in master_engines.items():
                FileHandler.write_file(
                    f"mapping_{prefix}_{self.output_file}", engine.mapping
                )

        print("Anonymization completely finished!")
