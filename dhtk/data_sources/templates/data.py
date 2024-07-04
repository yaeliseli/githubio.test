# coding=utf-8

"""Contains the Abstract Class Data."""

from abc import ABCMeta, abstractmethod


class Data(metaclass=ABCMeta):
    """Abstract method for search classes of the different catalog modules.

    This class should be used as parent for the classes implementing the search
    functions in submodules.

    Args:

    Returns:

    Raises:

    """

    @abstractmethod
    def search_by_author(self, author_name, author_last_name):
        """Data books in a catalog by author's name and last name.

        Args:
          author_last_name:
          author_name(str): Author's name or first name in plain text, case-insensitive.
        It can be a part of the author's name.
          author_last_name(str): Author's last name in plain text, case-insensitive.
        It can be a part of the author's last name.

        Returns:
          dhtk.templates.book.Book: An instance of the class Book

        Raises:


        """

        NotImplementedError(
            f"Class {self.__class__.__name__} doesn't implement search_by_author()"
        )

    @abstractmethod
    def search_by_title(self, title):
        """Data books by title.

        Args:
          title(str): Title in plain text, case-insensitive. It can be a part of the title.

        Returns:
          dhtk.templates.book.Book: An instance of the class Book

        Raises:


        """
        NotImplementedError(
            f"Class {self.__class__.__name__} doesn't implement search_by_title()"
        )

    @abstractmethod
    def get_metadata(self, item):
        """Get metadata about the book that is present in the catalog

        Args:
          item(dhtk.templates.book.Book || dhtk.templates.author.Author): An instance of the class Book or Author

        Returns:
          a dictionary of metadata:

        Raises:


        """

        NotImplementedError(
            f"Class {self.__class__.__name__} doesn't implement get_metadata()"
        )
