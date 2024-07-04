# coding=utf-8
"""Contains the GutenbergBook Class.
------------------------------------
Returns a Book object which is extended to contain parameters for gutenberg id
"""

import re
import logging
from abc import ABC

from dhtk.data_sources.gutenberg.api.texts import GutenbergTexts

from dhtk.data_sources.templates.book import Book
logger = logging.getLogger(__name__)


class GutenbergBook(Book):
    """Extends the Book class for Project Gutenberg books.


    Examples:
        >>> from pprint import pprint
        >>> from  dhtk.data_sources.gutenberg.api.book import GutenbergBook
        >>> from  dhtk.data_sources.gutenberg.api.author import GutenbergAuthor

        >>> moby_dick = GutenbergBook(
        >>>     title="Moby Dick",
        >>>    gutenberg_id="http://www.gutenberg.org/ebooks/2489",
        >>>    author=GutenbergAuthor(
        >>>         gutenberg_id='http://www.gutenberg.org/2009/agents/9',
        >>>         name='Melville, Herman'
        >>>     )
        >>> )

        >>> from dhtk.data_sources.gutenberg.api.data import GutenbergData

        >>> gutenberg_search = GutenbergData()
        >>> book = gutenberg_search.get_book("http://www.gutenberg.org/ebooks/2701")
        >>> book.print_info()
        # Title       : Moby Dick; Or, The Whale
        # Author      : Herman Melville
        # Metadata    :
        #     - gutenberg_id: http://www.gutenberg.org/ebooks/2701


    """

    def get_data_file_name(self):
        """

        Returns:

        """
        return f"{self.get_book_id_number()}.txt"

    def save_data_file_to(self, corpus_path):
        """

        Args:
            corpus_path:
        """
        self.get_repository().save_original_text_file_to(corpus_path / self.get_data_file_name())

    def __init__(self, gutenberg_id, title, author, same_as=None, **kwargs):
        """
        Init function of the GutenbergBook Class.

        Args:
        gutenberg_id (str) :  Must start with "http://www.gutenberg.org/ebooks/".

        author (dhtk.common.author.Author) :The object containing the author of the book.
                Of type dhtk.common.author.Author or a subclass of it.

        title (str) :The title of the book, in format given by Gutenberg.

        same_as (dict): A dictionary containing same_as URIs.

        **kwargs (dict) : Will be used as metadata.
        """
        if same_as is None:
            same_as = {}
        id_format = re.compile(r"http://www.gutenberg.org/ebooks/\d+$")
        if not id_format.fullmatch(gutenberg_id):
            # LOGGER.error("This gutenberg id is not valid! %s", gutenberg_id)
            raise ReferenceError(f"This gutenberg id is not valid! {gutenberg_id}")

        title = re.sub(r"\s+", " ", title)
        super().__init__(title=title, author=author, gutenberg_id=gutenberg_id, same_as=same_as, metadata=kwargs)
        self.metadata.update({
            "subject": self.metadata.get("gutenberg_subject", []),
            "bookshelf": self.metadata.get("gutenberg_bookshelf", [])
        })

    def get_book_id(self):
        """

        Returns:

        """

        return self.metadata.get("gutenberg_id", "")

    def get_uri(self):
        """

        Returns:

        """

        return self.metadata.get("gutenberg_id", "")

    def get_book_id_number(self):
        """

        Returns:

        """
        return self.metadata.get("gutenberg_id", "/").rsplit("/", 1)[1]

    def get_text_file_dir_path(self):
        """Return the suffix of the uri of the book in a gutenberg text repository.

        Args:

        Returns:
          str: Returns the suffix of the gutenberg file repository where the file is to be found:

        Args:

        Returns:

        Notes
        -----

        This method is generally used with::

            "file://gutenberg/repository/path/" + self.get_text_file_dir_path() + "-file.extension"
            #or
            "http://distant.gutenberg-repository.path" + self.get_text_file_dir_path() + "-file.extension"

        the "-file.extension" can be -0.txt, .zip, .txt depending on the presence in the repository
        and on the file encoding.

        Example
        -------

            print(book.get_text_file_dir_path())
            # "2/7/0/2701/2701"
        """
        # LOGGER.debug("id: %s", self.metadata.get("gutenberg_id", ""))
        gutenberg_id_num = self.get_book_id_number()
        if int(gutenberg_id_num) < 10:
            subdir = f"0/{gutenberg_id_num}/{gutenberg_id_num}"
        elif int(gutenberg_id_num) < 100:
            subdir = f"{gutenberg_id_num[0]}/{gutenberg_id_num}/{gutenberg_id_num}"
        elif int(gutenberg_id_num) < 1000:
            subdir = f"{gutenberg_id_num[0]}/{gutenberg_id_num[1]}/{gutenberg_id_num}/{gutenberg_id_num}"
        else:
            gutenberg_id_string = str(gutenberg_id_num).zfill(2)
            all_but_last_digit = list(gutenberg_id_string[:-1])
            subdir_part = "/".join(all_but_last_digit)
            subdir = f"{subdir_part}/{gutenberg_id_num}/{gutenberg_id_num}"
        return subdir

    def repository(self):
        """

        Returns:

        """
        repo = GutenbergTexts(self)

        return repo

    def original_text(self):
        """

        Returns:

        """
        text = self.repository().get_original_text()

        return text

    def __eq__(self, other):
        """
        Equality function.

        Notes
        -----
        Test the equality of the two books. Using the gutenberg_id if other is an instance of
        GutenbergBook. If not, it uses the dhtk.data_sources.templates.book.Book.__eq__() method that uses the
        book's authors and titles.

        Parameters
        ----------
            other: an instance from dhtk.data_sources.templates.book.Book or any child class.

        Returns
        -------
            equality: bool
        """
        if isinstance(other, GutenbergBook):
            equals = self.get_book_id() == other.get_book_id()
        else:
            equals = super().__eq__(other)
        return equals

    def __hash__(self):
        """
        Returns hash of attributes of gutenberg book.

        Notes
        -----
        The hash is created from:
            - author
            - title
            - first date (from metadata)
        Allows dictionary keys to be compared quickly.

        Returns
        -------
            hash: int
        """
        return hash(str(self.author.get_name()) + self.title + self.get_first_edition_date())

    def __repr__(self):
        """

        Returns
        -------
        object_str : String representing the object
        """

        return (f"<GutenbergBook: {self.get_author().get_name()} - "
                f"{self.get_title()} gutenberg_id: {self.get_book_id_number()}>")
