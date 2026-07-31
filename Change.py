#!/usr/bin/env python
import re

from faker import Faker


class BaseAnonymizer:
    def __init__(self, locale="ja_JP"):
        self.fake = Faker(locale)
        Faker.seed(196)
        self.mapping = {}

    def _get_or_create_fake(self, original_value, generator_func):
        """
        Retrieves an existing fake value or generates a new one using the provided function.
        """
        if original_value not in self.mapping:
            self.mapping[original_value] = generator_func()
        return self.mapping[original_value]

    def anonymize_text(self, strings_to_replace, text_content, generator_func):
        """
        Iterates through the target strings and replaces them in the text content.
        """
        for original_value in strings_to_replace:
            fake_value = self._get_or_create_fake(original_value, generator_func)
            text_content = re.sub(
                r"\b" + re.escape(original_value) + r"\b", fake_value, text_content
            )
        return text_content


class ChangeName(BaseAnonymizer):
    """
    Replacing the real name with an anonymized name
    """

    def get_real_name(self, strings_to_replace, text_content):
        return self.anonymize_text(strings_to_replace, text_content, self.fake.name)


class ChangeID(BaseAnonymizer):
    """ "
    Replacing the real ID with an anonymized ID
    """

    def get_real_id(self, strings_to_replace, text_content):
        return self.anonymize_text(strings_to_replace, text_content, self.fake.uuid4)
