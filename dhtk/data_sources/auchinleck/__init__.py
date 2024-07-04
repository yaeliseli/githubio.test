"""Auchinleck extension module"""


import warnings
import pickle
import os
from time import sleep
# from helpers import make_dirs
import pandas as pd

from http.client import RemoteDisconnected
from urllib.error import URLError

from dhtk.core.system import make_dirs, download_files
from dhtk.data_sources.blueprint import AbstractDataSource
from dhtk.data_sources.auchinleck.api.data import AuchinleckData

warnings.formatwarning = lambda message, *args: f"{message}\n"


class Module(AbstractDataSource):
    """Auchinleck Triplestore Class"""
    name = "auchinleck"
    storage_type = "triplestore"
    # data_file = "https://sandbox.zenodo.org/record/730187/files/auchinleck_data.rdf?download=1"
    data_file = "https://drive.switch.ch/index.php/s/IulLwm8odkj7JNU/download"

    @classmethod
    def get_data_file(cls, output_path, storage_type):
        if isinstance(cls.storage_type, str):
            data_file = cls.data_file
        else:
            data_file = cls.storage_type[cls.storage_type.index(storage_type)]
        download_files(data_file, output_path, "auchinleck_data.rdf")
        return output_path / "auchinleck_data.rdf"

    def __init__(self, working_directory, endpoints):

        # Defaults required to be defined for each extension

        # Get the extension
        self.wrapper = AuchinleckData(sparql_endpoint=endpoints[0])

        # Instantiate the list of results
        self._results = []

    def welcome(self):
        for check in range(10):
            try:
                stats = self.wrapper.statistics()
                break
            except (RemoteDisconnected, URLError):
                if check >= 9:
                    warnings.warn("WARNING: There is a problem with the connection!")
                    print("Probably Docker is slow to restart!")
                    break
                sleep(10)

    def get(self, what, option, custom_option=None, add=False):
        """
        Extension wrapper method to call all DHTK functionalities with a simple syntax

        Examples
        -------
            ::

            get('word list','French)

            get('manuscript years', 'king')

            get('poem lexicon', 'Sir Tristrem')

            get(
                'custom query',
                'SELECT ?subject ?predicate ?object WHERE {?subject ?predicate ?object} LIMIT 25',
                ['subject', 'predicate', 'object']
            )

        Parameters
        ----------
        what: string
            Type of information to retrieve.
            Possible values are:
            - 'word list' to search for a list of words of a specific etymology
            - 'manuscript years' to search for the earliest years a word appeared in Middle English (based on manuscripts)
            - 'composition years' to search for the earliest years a word appeared in Middle English (based on composition)
            - 'dictionary form' to search for the dictionary form of a word in the Middle English Dictionary
            - 'poem lexicon' to search for the lexicon words of a specific poem
            - 'custom query' to search for the database using a custom SPARQL query
        option: string
            Options for the type of information to retrieve. If 'what' parameter value is:
            - 'word list' options must be one of the etymologies, that is, 'French', 'English', 'Latin', 'Scandinavian', 'Unknown', 'Other'
            - 'manuscript years', 'composition years', 'dictionary form' require a word of the Auchinleck lexicon, as a string.
            - 'poem lexicon' option must be the title of one of Auchinleck poems, as a string.
            - 'custom query' option
        custom_option: list
            This parameter is to be used only with a custom query. The option must be a list of the desired variables
            to be searched by the custom SPARQL query.

        Returns
        -------
        Requested information from Auchinleck dataset as a list of dictionaries
        """
        if not custom_option:
            custom_option = []

        # Prepare arguments
        option = option.strip().lower()
        what = what.strip().lower()

        if what == "words list":
            if option == "french":
                response = self.wrapper.get_french_words()
            elif option == "english":
                response = self.wrapper.get_english_words()
            elif option == "latin":
                response = self.wrapper.get_latin_words()
            elif option == "scandinavian":
                response = self.wrapper.get_scandinavian_words()
            elif option == "other":
                response = self.wrapper.get_other_words()
            elif option == "unknown":
                response = self.wrapper.get_unknown_words()
            else:
                warnings.warn("Not a valid option")
                print("Allowed options for words list are:"
                      "\nFrench\nEnglish\nLatin\nScandinavian\nOther\nUnknown")
                return
        elif what == "manuscript years":
            if option.isalnum():
                response = self.wrapper.get_manuscript_year(option)
            else:
                warnings.warn("Not a valid option")
                print("Allowed option for manuscript years is a string (lexicon word)")
                return
        elif what == "composition years":
            if option.isalnum():
                response = self.wrapper.get_composition_year(option)
            else:
                warnings.warn("Not a valid option")
                print("Allowed option for composition years is a string (lexicon word)")
                return
        elif what == "dictionary form":
            if option.isalnum():
                response = self.wrapper.get_manuscript_year(option)
            else:
                warnings.warn("Not a valid option")
                print("Allowed option for dictionary form is a string (lexicon word)")
                return
        elif what == "poem lexicon":
            if option.isalnum():
                response = self.wrapper.get_poem_lexicon(option)
            else:
                warnings.warn("Not a valid option")
                print("Allowed option for poem lexicon is a string (poem title)")
                return
        elif what == "custom query":
            if type(custom_option) is list:
                response = self.wrapper.get_custom_query(option, custom_option)
            else:
                warnings.warn("Not a valid option")
                print("Allowed options for custom query is a string and a list")
                return
        else:
            warnings.warn("Not a valid option")
            print("""Allowed arguments are
            \nwords list\nmanuscript years\ncomposition years\ndictionary form
            \npoem lexicon\ncustom query""")
            return

        if not response:
            response = "\n".join([f"No {what} found.",
                                  "Please make sure there are no spelling mistakes."])
            print(response)
            return
        else:
            self._results = response
            return response

    def save(self):
        """
        Saves the requested information from the Auchinleck dataset as pandas.DataFrame
        to a pickle dump.

        """

        # Prepare save directory
        path = os.getcwd()

        # Save Python Query Object
        with open(path + "results.pk", 'wb') as pickled_file:
            pickle.dump(pd.DataFrame(self._results), pickled_file, protocol=pickle.HIGHEST_PROTOCOL)
        pickled_file.close()

    def search(self, what, name_or_id):
        pass