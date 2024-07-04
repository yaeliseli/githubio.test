# coding=utf-8
"""Gutenberg extension data_source"""
import logging
import warnings
from http.client import RemoteDisconnected
from time import sleep
from urllib.error import URLError

from dhtk.core.system import download_files
from dhtk.data_sources.blueprint import AbstractDataSource
from .api.data import GutenbergData

logger = logging.getLogger(__name__)

warnings.formatwarning = lambda message, *args: f"{message}\n"


class Module(AbstractDataSource):
    """Gutenberg Triplestore Class"""
    name = "gutenberg"
    storage_type = "triplestore"
    data_file = "https://drive.switch.ch/index.php/s/IulLwm8odkj7JNU/download"


    @classmethod
    def get_data_file(cls, output_path, storage_type):
        """
        Get a content as defined in self.data_file and write into a file into output_path
        Args:
            output_path (Path): the path where to write (i.e. output_path = Path('WD/gutenberg/data/triplestore'))
            storage_type (str): the type of the storage

        Returns:
            Path: the path to the file with data

        """
        # output_path can be like this output_path = 'WD/gutenberg/data/triplestore'
        # storage_type can be like this storage_type= 'triplestore'
        if isinstance(cls.storage_type, str):
            data_file = cls.data_file
        else:
            data_file = cls.storage_type[cls.storage_type.index(storage_type)]
        download_files(data_file, output_path, "gutenberg.ttl")
        return output_path / "gutenberg.ttl"

    def __init__(self, working_directory, endpoints):

        # Get the extension
        self.wrapper = GutenbergData(sparql_endpoint=endpoints[0])
        self.types = ["author", "book", "shelf", "subject"]

    def welcome(self):
        """

        """
        stats = None
        for check in range(10):
            try:
                stats = self.wrapper.statistics()
                break
            except (RemoteDisconnected, URLError, ConnectionResetError):
                if check >= 9:
                    warnings.warn("WARNING: There is a problem with the connection!")
                    print("Probably Docker is slow to restart!")
                    stats = "\nNo statistics available"
                    break
                sleep(10)
        print(stats)

    def get(self, what, name_or_id):
        """
        Extension wrapper method to call all DHTK functionalities with a simple syntax

        Parameters
        ----------
        what: string
            Type of information to retrieve.
            DHTK Gutenberg has the options to search for books, authors, shelves and subjects
        name_or_id: string
            Name identifying the specific information to retrieve.

        Returns
        -------
        Requested book information from Gutenberg dataset
        """
        dispatch = {
            "book_id": self.wrapper.get_book,
            "book": self.wrapper.search_by_title,
            "author_id": self.wrapper.get_author,
            "author": self.wrapper.search_by_author,
            "shelf": self.wrapper.search_by_bookshelf,
            "subject": self.wrapper.search_by_subject,
        }
        try:
            if what in dispatch:
                if isinstance(name_or_id, str):
                    results = dispatch[what](name_or_id, works=True)
                else:
                    results = dispatch[what](*name_or_id, works=True)
                return results
        except ValueError as error:
            valid = '", "'.join(list(dispatch.keys()))
            raise ValueError(
                f'Could not find what you are searching for, valid entries for "what" are:\n["{valid}"]'
            ) from error

    def search(self, what, name_or_id="all"):
        """

        Args:
            what:
            name_or_id:

        Returns:

        """
        dispatch = {
            "book_id": self.wrapper.get_book,
            "book": self.wrapper.search_by_title,
            "author_id": self.wrapper.get_author,
            "author": self.wrapper.search_by_author,
            "shelf": self.wrapper.search_by_bookshelf,
            "subject": self.wrapper.search_by_subject,
            "all_book": self.wrapper.all_books,
            "all_author": self.wrapper.all_authors,
            "all_subject": self.wrapper.all_subjects,
            "all_shelf": self.wrapper.all_bookshelves,
        }

        try:
            if name_or_id == "all":
                what = "all_" + what
                if what in dispatch:
                    return dispatch[what]()
            elif what in dispatch:
                if isinstance(name_or_id, str):
                    results = dispatch[what](name_or_id, works=False)
                else:
                    results = dispatch[what](*name_or_id, works=False)
                return results
        except ValueError as error:
            valid = '\", \"'.join([value for value in dispatch if not value.startswith('all_')])
            raise ValueError(
                f'Could not find what you are searching for, valid entries for "what" are:\n["{valid}"]'
            ) from error

    def query(self, query):
        """

        Args:
            query:

        Returns:

        """
        return self.wrapper.query(query)
