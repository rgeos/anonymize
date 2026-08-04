#!/usr/bin/env python
import re
import string
import secrets
from faker import Faker
from NameProvider import NameProvider
from faker_healthcare import HealthcareProvider

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
    def __init__(self, locale="ja_JP", last_name_path=None, first_name_path=None):
        self.fake = Faker(locale)
        self.locale = locale
        Faker.seed(196)
        self.alphanumeric_pool = string.ascii_letters + string.digits

        # add a custom name provider
        if last_name_path or first_name_path:
            provider = NameProvider(self.fake, last_name_path, first_name_path)
            self.fake.add_provider(provider)

        # register the healthcare provider
        self.fake.add_provider(HealthcareProvider)

    def get_name_strategy(self):
        if hasattr(self.fake, "generate_full_name"):
            seen = set()

            def unique_custom_name():
                for _ in range(1000):  # Prevent infinite loops if names run out
                    name = self.fake.generate_full_name()
                    if name not in seen:
                        seen.add(name)
                        return name
                return self.fake.generate_full_name()

            return unique_custom_name
        return lambda: self.fake.unique.name()
        # the old implementation to ensure uniqueness
        # return (
        #     lambda: f"{self.fake.last_name()} {self.fake.first_name()} {''.join(random.choice(self.alphanumeric_pool) for _ in range(3))}"
        # )

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

    def get_disease_strategy(self):
        return lambda: f"{self.fake.disease()}_{self.fake.icd10_code()} : {self.fake.medical_procedure()}"
