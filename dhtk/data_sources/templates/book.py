# coding=utf-8
# coding=utf-8

"""Contains the class describing a dhtk book."""
import abc
import logging
import pathlib
from abc import ABCMeta

from dhtk.corpus.work import Work

logger = logging.getLogger(__name__)


class Book(Work, metaclass=ABCMeta):
    """The general book class of dhtk.

    Books implemented in submodules of dhtk should have this class as parent.

    Example
    -------

        from pprint import pprint

        from dhtk.templates.book import Book

        mrs_dalloway_book = Book(
            "Mrs Dalloway",
            "Virginia Woolf",
            metadata = {
                "publisher": "Hogarth Press",
                "published": "14 May 1925",
                "first_edition_date": "14 May 1925",
                "country": "United Kingdom",
            },
            language="English",
            ISBN="0-15-662870-8",
            same_as={"http://dbpedia.org/page/Mrs_Dalloway": "User"}
        )

    Args:

    Returns:

    Raises:

    """

    get_repository = None

    def __init__(
            self,
            title,
            author="Anonymous",
            metadata=None,
            author_metadata=None,
            **kwargs
    ):
        """
        Init function of a Book.
        ------------------------

        Parameters
        ----------
        author : dhtk.templates.author.Author || str
            The author of the book.

        title : str
            required, the book's title

        metadata: dict
            Contains all found metadata relative to the book.
            can include:

                - number of pages
                - editor
                - publisher
                - first edition date

        author_metadata : dict
            a dict that holds the metadata about the author.

        Returns
        -------
        book : dhtk.templates.book.Book
            A Book object
        """
        Work.__init__(self, title, author, metadata=metadata, author_metadata=author_metadata)
        logger.debug("Book init args %s", (title, author, metadata, author_metadata, kwargs))

        self.metadata.update(kwargs)

    def get_editor(self):
        """Return the book's editor.

        The value corresponding to the key "editor" in dict metadata for Book

        Args:

        Returns:
          str: The editor of the book

        Raises:


        """
        return self.metadata.get("editor", "")

    def get_publisher(self):
        """Returns the book's publisher.

        The value corresponding to the key "publisher" in dict metadata for Book

        Args:

        Returns:
          str: The publisher of the book
          Example:
          -------: mrs_dalloway_book.get_publisher()
          # 'Hogarth Press'

        Raises:


        """
        return self.metadata.get("publisher", "")

    def get_first_edition_date(self):
        """Returns the first edition date of the book:
        value corresponding to the key "first_edition_date" in dict metadata for Book

        Args:

        Returns:
          str:
          Example:
          -------: mrs_dalloway_book.get_first_edition_date()
          # '14 May 1925'

        Raises:


        """
        return self.metadata.get("first_edition_date", "")

    def get_number_of_pages(self):
        """Return the number of pages of the book.

        Args:

        Returns:
          int:

        Raises:


        """
        return self.metadata.get("number_of_pages", -1)

    def get_data_file_name(self):
        """Return a good filename for a book.

        Args:

        Returns:
          Example:
          -------: mrs_dalloway_book.get_text_file_name()
          # 'Virginia_Woolf-Mrs_Dalloway.txt'

        Raises:


        """

        file_name = self.get_author().get_full_name() + "-" + self.get_title() + ".txt"
        return file_name.replace(" ", "_")

    def __eq__(self, other):
        """
        Equality function.
        Ensures that two given books are not identical. Avoids redundancy.
        Compares author and title.

        Parameters
        ----------
        other: dhtk.templates.book.Book
             different book object from the book object calling the class.

        Return
        ------
            equal: bool
        """
        return self.author == other.get_author() and self.title == other.get_title()

    def __ne__(self, other):
        """
        Inequality function. Overrides __eq__. Is false if __eq__ is true and vice versa.

        Parameters
        ----------
        other: dhtk.templates.book.Book

        Return
        ------
            not_equal: bool
        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        Returns hash of attributes of Book:
            - author from author.Author
                object
            - title
                str
            - first date (from metadata)
                date
        Allows dictionary keys to be compared quickly.

        Returns
        -------
            hash: int
        """
        return hash((self.author, self.title, self.get_first_edition_date()))

    def __repr__(self):
        """

        Returns
        -------
        object_str : str
            String representing the object
        """
        author = self.get_author()

        if isinstance(author, str):
            return f"<Book: {author} - {self.get_title()}>"

        return f"<Book: {author.get_full_name()} - {self.get_title()}>"
