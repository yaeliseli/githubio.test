# coding=utf-8


# noinspection PyUnusedFunction
import copy


class Metadata:
    """

    """
    def __init__(self, metadata: dict):
        self.__metadata = {}
        if metadata:
            if isinstance(metadata, dict):
                self.__metadata = metadata
            elif hasattr(metadata, "to_dict"):
                self.__metadata = metadata.to_dict()
            else:
                raise TypeError("Metadata should be a dict or have a method to_dict()")

    def get_metadata(self):
        return self.__metadata

    def update(self, metadata: dict):
        """

        Args:
            metadata:
        """
        if not metadata:
            return
        new_keys = set(metadata.keys())
        old_keys = self.__metadata
        old_keys = set(old_keys.keys())
        for key in new_keys - old_keys:
            self.__metadata[key] = metadata.pop(key)
        for key in old_keys.intersection(new_keys):
            old_value = self.__metadata[key]
            new_value = metadata[key]
            if old_value == new_value:
                continue
            if not old_value:
                self.__metadata[key] = new_value
            elif isinstance(old_value, str) or str(old_value).isnumeric():
                if isinstance(new_value, list):
                    self.__metadata[key] = new_value.insert(0, old_value)
                else:
                    self.__metadata[key] = [new_value, old_value]
            elif isinstance(old_value, dict):
                self.__metadata.update(**new_value)
            elif isinstance(new_value, str) or str(new_value).isnumeric():
                self.__metadata[key] = old_value.append(new_value)

    def get(self, key, default=None):
        return self.__metadata.get(key, default)

    def __getitem__(self, item):
        return self.get(item)

    def print_info(self):
        """

        """
        print(f"{'Metadata':12}:")
        for key, value in sorted(self.__metadata.items()):
            if isinstance(value, str):
                print(4 * " " + f"- {key:12}: {value:>12}")
            elif isinstance(value, dict):
                print(4 * " " + f"- {key:12}:")
                for entry in sorted(value.values()):
                    print(12 * " " + f"- {entry}")
            elif value:
                print(4 * " " + f"- {key:12}:")
                for entry in sorted(value):
                    print(12 * " " + f"- {entry}")

    def to_dict(self):
        """

        Returns:

        """
        metadata = {}
        for key, value in self.__metadata.items():
            if isinstance(value, set):
                metadata[key] = value
            else:
                metadata[key] = value
        return metadata

    def to_pandas_dataframe(self):
        """Convert the book's information into a pandas.DataFrame.

        Args:

        Returns:
          pandas.DataFrame:

        Example:

        Raises:


        """
        import pandas as pd
        return pd.DataFrame([self.to_dict()])
