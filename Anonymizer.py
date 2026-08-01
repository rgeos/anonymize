#!/usr/bin/env python
import re
import string
import secrets
from faker import Faker


class Anonymizer:
    def __init__(self, target_terms, strategy_func):
        self.term_set = set(target_terms)
        self.mapping = {}
        self.regex = None

        if not target_terms:
            return

        for term in target_terms:
            if term in self.mapping:
                continue

            self.mapping[term] = strategy_func()

        escaped_terms = [re.escape(t) for t in target_terms]
        pattern = r"\b(" + "|".join(escaped_terms) + r")\b"
        self.regex = re.compile(pattern)

    def process_line(self, line):
        if not self.regex:
            return line

        words = re.findall(r"\b\w+\b", line)
        if not self.term_set.intersection(words):
            return line

        return self.regex.sub(lambda match: self.mapping[match.group(0)], line)


class AnonymizationStrategies:
    def __init__(self, locale="ja_JP"):
        self.fake = Faker(locale)
        Faker.seed(196)
        self.alphanumeric_pool = string.ascii_letters + string.digits

    def get_jp_name_strategy(self):
        """Returns a strategy function for unique names with a 3-char suffix."""

        def strategy():
            while True:
                try:
                    core_name = self.fake.unique.name()
                    suffix = "".join(
                        secrets.choice(self.alphanumeric_pool) for _ in range(3)
                    )
                    return f"{core_name} {suffix}"
                except Exception:
                    self.fake.unique.clear()

        return strategy

    def get_name_strategy(self):
        return lambda: self.fake.unique.name()

    def get_uuid_strategy(self):
        return lambda: self.fake.unique.uuid4()

    def get_email_strategy(self):
        return lambda: self.fake.unique.company_email()

    def get_phone_strategy(self):
        return lambda: self.fake.unique.phone_number()
