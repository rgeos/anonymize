from faker.providers import BaseProvider
from FileHandler import FileHandler


class NameProvider(BaseProvider):
    def __init__(self, generator, last_name_path, first_name_path):
        super().__init__(generator)
        self.last_names = (
            FileHandler.read_file(last_name_path) if last_name_path else []
        )
        self.first_names = (
            FileHandler.read_file(first_name_path) if first_name_path else []
        )

    def generate_full_name(self):
        last = self.random_element(self.last_names) if self.last_names else "LastName"
        first = (
            self.random_element(self.first_names) if self.first_names else "FirstName"
        )
        return f"{last} {first}"

    def generate_last_name(self):
        return self.random_element(self.last_names) if self.last_names else "LastName"

    def generate_first_name(self):
        return (
            self.random_element(self.first_names) if self.first_names else "FirstName"
        )
