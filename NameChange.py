#!/usr/bin/env python
import re

from faker import Faker


class NameChange:
    """
    Replacing the real name with an anonymized name
    """

    def __init__(self, locale="ja_JP"):
        self.fake = Faker(locale)
        self.name_mapping = {}

        Faker.seed(196)

    def set_fake_name_to(self, original_name):
        """
        Create a fake name
        """
        if original_name not in self.name_mapping:
            self.name_mapping[original_name] = self.fake.name()
        return self.name_mapping[original_name]

    def get_real_name(self, strings_to_replace, text_content):
        """
        Replaces the real name with an anonymized name
        """
        for original_name in strings_to_replace:
            fake_name = self.set_fake_name_to(original_name)
            text_content = re.sub(
                r"\b" + re.escape(original_name) + r"\b", fake_name, text_content
            )
        return text_content
