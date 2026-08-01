#!/usr/bin/env python
import re
import string
import secrets
import random
from faker import Faker

# Global worker space parameters initialized safely by the pool
_worker_mappings = {}
_compiled_patterns = []


def init_worker(master_mappings):
    """
    Runs once upon worker birth. Receives the pre-compiled static
    mapping dictionary from the master thread.
    """
    global _worker_mappings, _compiled_patterns
    _worker_mappings = master_mappings
    _compiled_patterns = []

    for prefix, term_map in master_mappings.items():
        if not term_map:
            continue

        sorted_terms = sorted(term_map.keys(), key=len, reverse=True)
        escaped = [re.escape(t) for t in sorted_terms]
        pattern = re.compile(r"(?<!\w)(" + "|".join(escaped) + r")(?!\w)")

        _compiled_patterns.append((pattern, term_map))


def worker_process_chunk(lines):
    """Processes individual lines cleanly without regex backtracking crashes."""
    processed_lines = []
    for line in lines:
        current_line = line
        for pattern, term_map in _compiled_patterns:
            current_line = pattern.sub(
                lambda m: term_map.get(m.group(0), m.group(0)), current_line
            )
        processed_lines.append(current_line)
    return processed_lines


class Anonymizer:
    def __init__(self, locale="ja_JP"):
        self.fake = Faker(locale)
        Faker.seed(196)
        self.alphanumeric_pool = string.ascii_letters + string.digits

    def get_jp_name_strategy(self):
        return (
            lambda: f"{self.fake.last_name()} {self.fake.first_name()} {''.join(random.choice(self.alphanumeric_pool) for _ in range(3))}"
        )

    def get_uuid_strategy(self):
        return lambda: self.fake.uuid4()

    def get_company_strategy(self):
        return lambda: self.fake.company()

    def get_random_hash_strategy(self):
        return lambda: secrets.token_hex(8)

    def get_email_strategy(self):
        return lambda: self.fake.company_email()

    def get_phone_strategy(self):
        return lambda: self.fake.phone_number()
