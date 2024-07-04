# coding=utf-8

"""Contains the Abstract TextRepository Class."""

from abc import ABCMeta, abstractmethod


# noinspection PyUnusedClass
class TextRepository(metaclass=ABCMeta):
    """Abstract TextRepository Class.

    This class should be used as parent class for the text repositories of subclasses.

    Args:

    Returns:

    Raises:

    """

    def __init__(self, repository_uri):
        """
        Init function of the repository class.

        Parameters
        ----------
        repository_uri :
            This uri can be of a directory (preceded by file) or remote location (http:)
        """
        self._repository_uri = repository_uri

    @abstractmethod
    def get_original_text(self, book):
        """Return the original text of the book.

        Args:
          book(dhtk.templates.book.Book): An instance of class Book in dhtk.templates.book

        Returns:
          str: Text of the book as formatted in http://aleph.gutenberg.org/1/3/0/0/13000/13000.txt

        Raises:


        """
        NotImplementedError(
            f"Class %s doesn't implement get_original_text(): {self.__class__.__name__}"
        )

    @abstractmethod
    def get_clean_text(self, book):
        """Return a clean version of the text. Remove headers, footers, notes, and annotations.

        Args:
          book(dhtk.templates.book.Book): An instance of class Book in dhtk.templates.book

        Returns:
          str: Clean version of the text.

        Raises:


        """
        NotImplementedError(
            f"Class %s doesn't implement get_clean_text(): {self.__class__.__name__}"
        )

    @abstractmethod
    def save_clean_text_file_to(self, book, destination):
        """Save a clean version of the text to destination.

        Remove headers, footers, notes, and annotations.
        Save a clean version of the text to destination.

        Args:
          book(dhtk.templates.book.Book): An instance of class Book in dhtk.templates.book
          destination:

        Returns:
          str: Path of the saved file.

        Raises:


        """
        NotImplementedError(
            f"Class %s doesn't implement save_clean_text_file_to(): {self.__class__.__name__}"
        )
