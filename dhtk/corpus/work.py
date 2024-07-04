# coding=utf-8

import abc
import pathlib

from .metadata import Metadata
from .author import Author


# noinspection PyUnusedFunction
class Work(metaclass=abc.ABCMeta):
    """

    """
    def __init__(self, title, author, metadata=None, author_metadata=None):

        self.metadata = Metadata(metadata)

        self.title = title

        if isinstance(author, Author):
            self.author = author
            self.author.metadata.update(author_metadata)
        else:
            self.author = Author(name=author, metadata=author_metadata)

    def get_data_file(self, corpus_path: pathlib.Path) -> pathlib.Path:
        """

        Args:
            corpus_path:

        Returns:

        """
        return corpus_path / self.get_data_file_name()

    @abc.abstractmethod
    def get_data_file_name(self) -> str:
        """

        """
        raise NotImplementedError("Please implement a get_data_file_name method")

    def set_author(self, author, author_metadata):
        """

        Args:
            author:
            author_metadata:
        """
        if isinstance(author, Author):
            self.author = author
            self.author.metadata.update(author_metadata)
        else:
            self.author = Author(name=author, metadata=author_metadata)

    def get_author(self):
        """

        Returns:

        """
        return self.author

    def get_title(self):
        """

        Returns:

        """
        return self.title

    def save_data_file_to(self, corpus_path: pathlib.Path) -> None:
        """

        Args:
            corpus_path:
        """
        raise NotImplementedError("Please implement a save_data_file_to(corpus_path) method")

    def print_info(self):
        """Print information about the author.

        Args:

        Returns:

        Raises:

        Examples:
            print_info of Charles Dickens infos returns a print with his names, birthdate,
            biography and bibliography.

                charles_dickens_author.print_info()
                # Charles John Huffam Dickens
                # Metadata    :
                #     - birth_date  :   07/02/1812
                #     - death_date  :   09/06/1870
                #     - biography   : Charles John Huffam Dickens (/ˈdɪkɪnz/; 7 February 1812 – ...)
                #     - bibliography:
                #             - Great Expectations
                #             - Oliver Twist
                #             - David Copperfield
                #             - Bleak House
                #     - name        : Charles John Huffam Dickens
                #     - first_name  :      Charles
                #     - middle_name :  John Huffam
                #     - last_name   :      Dickens


        """
        print(f"{'Title':12}: {self.get_title()}")
        print(f"{'Author':12}: {self.get_author().get_full_name()}")
        self.metadata.print_info()

    def to_dict(self):
        """Convert to python dict for general purpose.

        Args:

        Returns:
          dict:
          Example:
          -------: pprint(mrs_dalloway_book.to_dict())
          # {'author_first_name': 'Virginia',
          # 'author_last_name': 'Woolf',
          # 'author_middle_name': '',
          # 'author_name': 'Virginia Woolf',
          # 'bookISBN': '0-15-662870-8',
          # 'book_title': 'Mrs Dalloway',
          # 'book_country': 'United Kingdom',
          # 'book_first_edition_date': '14 May 1925',
          # 'book_language': 'English',
          # 'book_published': '14 May 1925',
          # 'book_publisher': 'Hogarth Press'}

        Raises:


        """

        work_dict = self.metadata.to_dict()
        work_dict["title"] = self.get_title()
        work_dict["author"] = self.get_author().to_dict()
        return work_dict

    def to_pandas_dataframe(self):
        """Convert the author's information into a pandas.DataFrame.

        Args:

        Returns:
          pd.DataFrame: pandas_dataframe->

        Raises:

        """
        import pandas as pd
        return pd.DataFrame([self.to_dict()])

    def __hash__(self):
        raise NotImplementedError("Please implement a __hash__ method")

    def __ne__(self, other):
        raise NotImplementedError("Please implement a __ne__ method")

    def __eq__(self, other):
        raise NotImplementedError("Please implement a __eq__ method")

    def __lt__(self, other):
        return self.title < other.title

    def __le__(self, other):
        return self.title <= other.title

    def __gt__(self, other):
        return self.title > other.title

    def __ge__(self, other):
        return self.title >= other.title
