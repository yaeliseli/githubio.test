# coding=utf-8
"""Abstract class to be used as template for new extension modules __init__ script"""

# Import dependencies
import abc
import warnings
import logging

import typing

from dhtk.corpus.work import Work
logger = logging.getLogger(__name__)

warnings.formatwarning = lambda message, *args: f"{message}\n"


# noinspection PyUnusedFunction
class AbstractDataSource(metaclass=abc.ABCMeta):
    """
    Abstract Class that serves as a blueprint for the DHTK extension modules
    and additional datasets. All new data_sources inheriting from this class must define:

    Attributes:
        name (str): Name of the DHTK extension
        data_file (str) : URL to the DHTK extension RDF file to be downloaded

    Methods:
        get_data_file : A method saves the data_file to the output_path

    """

    # noinspection PyPropertyDefinition
    @property
    @classmethod
    @abc.abstractmethod
    def name(cls):
        """
        Class property that defines the name of the module.
        """
        return NotImplementedError("""
        Please define the modules name!
        """.replace(r"\t", ""))

    # noinspection PyPropertyDefinition
    @property
    @classmethod
    @abc.abstractmethod
    def storage_type(cls):
        """
        Class property that defines the storage type(s) used by the module.
        """
        return NotImplementedError("""
        Please define a storage type or storage types!

        Valid entries are: "sql", "nosql", "triplestore", "embedded".
        Use "embedded" : If the data source uses internal storage.


        EXAMPLES:
          storage_type = "triplestore"
          storage_type = ("sql", "nosql")
          storage_type = ["sql", "nosql", "triplestore"]
        """.replace(r"\t", ""))

    # noinspection PyPropertyDefinition
    @property
    @classmethod
    @abc.abstractmethod
    def data_file(cls):
        """
        Class property that defines the path(s) of the files to load to storage.
        """
        pass  # pylint: disable=unnecessary-pass

    @classmethod
    @abc.abstractmethod
    def get_data_file(cls, output_path, storage_type):
        """
        Class method that saves the data_file to the output_path

        Args:
            output_path (str): the path where to save the data file
            storage_type (str): The type of chosen storage

        Returns:

        """

        pass  # pylint: disable=unnecessary-pass

    @abc.abstractmethod
    def get(self, what: str, name_or_id: str) -> typing.Union[Work, typing.List[Work], NotImplementedError]:
        """
        Return a Work or a list of works.

        Args:
            what: The name of the type of metadata searched.
            name_or_id: The name or id of the work or author or other metadata searched.
            add: Determines if the results should be added to the corpus.

        Returns:
            A work or a list of works.
        """
        return NotImplementedError("Please implement a get method.")

    @abc.abstractmethod
    def search(self, what: str, name_or_id: str):
        """
        Search the data for names and ids.
        Args:
            what:
            name_or_id:

        Returns:

        """
        return NotImplementedError("Please implement a search method.")
