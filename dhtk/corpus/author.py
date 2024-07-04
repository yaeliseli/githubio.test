# coding=utf-8

from nameparser import HumanName
from .metadata import Metadata


class Author:
    """The class for a generic author.

    An Author is defined by his name and by various metadata,
    which may contain his birthdate, biography or bibliography.

    This class should be the parent to all authors used with the dhtk library.

    Args:

    Returns:

    Raises:

    Notes:
    This is the basic Author class, it serves as parent class for all Author
    classes found in the catalogs (for example:
    dhtk.data_sources.gutenberg.author.GutenbergAuthor).

    Examples:
        Model example to be used for further uses in the class.

            from pprint import pprint

            from nameparser import HumanName

            from dhtk.templates.author import Author

            charles_dickens_author = Author(
                HumanName("Charles John Huffam Dickens"),
                metadata=dict(),
                birth_date="07/02/1812",
                death_date="09/06/1870",
                biography=\
                "Charles John Huffam Dickens (/ˈdɪkɪnz/; 7 February 1812 – 9 June 1870) was an " \
                "English writer and social critic. He created some of the world's best-known " \
                "fictional characters and is regarded by many as the greatest novelist of the" \
                "Victorian era. His works enjoyed unprecedented popularity during his lifetime, " \
                "and by the 20th century critics and scholars had recognised him as a literary " \
                "genius. His novels and short stories are still widely read today.",
                bibliography=[
                    "Great Expectations",
                    "Oliver Twist",
                    "David Copperfield",
                    "Bleak House ",
                ],
                same_as={
                    'http://dbpedia.org/page/Charles_Dickens': 'User',
                    'https://viaf.org/viaf/88666393/': 'User'
                }
            )
    """

    def __init__(self, name, metadata=None, **kwargs):
        """
        The init function of the Author class.

        Parameters
        ----------
        name : nameparser.HumanName || str
            The name of the author as nameparser.HumanName object or a string.
        metadata : dict
            A dictionary containing the metadata.
        kwargs : dict
            Any other information.
        """

        self.metadata = Metadata(metadata)

        if kwargs:
            self.metadata.update(kwargs)

        if isinstance(name, str):
            name = HumanName(name)

        if not isinstance(name, HumanName):
            raise ValueError("Name is not an instance of nameparser.HumanName")

        self.name = name

    def get_full_name(self):
        """Get author's full name.

        Args:
            self

        Returns:
          str: full_name->     The author's full name.

        Raises:

        """
        return str(self.name)

    def get_name(self):
        """

        Returns:

        """
        return self.name

    def get_first_name(self):
        """Get author's first name.

        Args:

        Returns:
          str: first_name->     The author's first name.

        Raises:

        """
        return self.name.first

    def get_middle_name(self):
        """Get author's middle name.

        Args:

        Returns:
          str: middle_name->     The author's middle name.

        Raises:

        """
        return self.name.middle

    def get_last_name(self):
        """Get author's last name.

        Args:

        Returns:
          str: last_name->     The author's last name.

        Raises:

        """
        return self.name.last

    def get_birth_date(self):
        """Get author's birthdate.

        Args:

        Returns:
          str: birth_date->     The author's birthdate.

        Raises:

        """
        return self.metadata.get("birth_date", "")

    def get_death_date(self):
        """Get author's death date.

        Args:

        Returns:
          str: death_date->     The author's death date.

        Raises:

        """
        return self.metadata.get("death_date", "")

    def get_biography(self):
        """Get author's biography.

        Args:

        Returns:
          str: biography->     The author's biography.

        Raises:

        """
        return self.metadata.get("biography", "")

    def get_bibliography(self):
        """Get author's bibliography.

        Args:

        Returns:
          str: bibliography->     The author's bibliography.

        Raises:

        """
        return self.metadata.get("bibliography", "")

    def get_same_as(self):
        """Return gathered metadata.

        Args:

        Returns:
          dict: same_as->     The key is the uri of the same_as
          The value is the name of the source of the uri.

        Raises:

        """
        return self.metadata.get("same_as", [])

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
        print(self.get_name())
        self.metadata.print_info()

    def to_dict(self):
        """Convert to python dict for general purpose.

        Args:

        Returns:
          dict: author_as_dict->     A dictionary version of the Author's data.

        Raises:

        """
        author_dict = {}
        for key, value in self.metadata.to_dict().items():
            if isinstance(value, set):
                value = list(value)
            author_dict["metadata_" + key] = value

        author_dict["name"] = str(self.get_name())
        author_dict["first_name"] = self.get_first_name()
        author_dict["middle_name"] = self.get_middle_name()
        author_dict["last_name"] = self.get_last_name()
        return author_dict

    def to_pandas_dataframe(self):
        """Convert the author's information into a pandas.DataFrame.

        Args:

        Returns:
          pd.DataFrame: pandas_dataframe->

        Raises:

        """
        import pandas as pd
        return pd.DataFrame([self.to_dict()])

    def __eq__(self, other):
        """
        Equality function between authors.

        Test with a bool if two objects are equal in every aspect or not.

        Parameters
        ----------
        other : dhtk.templates.author.Author
            Another object of type Author.


        """
        result = self.get_first_name() == other.get_first_name()
        result = result and self.get_last_name() == other.get_last_name()
        result = result and self.get_birth_date() == other.get_birth_date()
        return result

    def __ne__(self, other):
        """
        Inequality function between authors.

        Test with a bool if two author instances are different in at
        least one aspect.

        Parameters
        ----------
        other : dhtk.templates.author.Author
            Another object of type Author.

        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        Return hash for the author.

        Returns
        -------
        hash : int

        """
        return hash(self.name.first + self.name.last + self.get_birth_date())

    def __repr__(self):
        """

        Returns
        -------
        object_str : str
            String representing the object
        """
        if self is not None:
            return f"<Author: {self.get_name()}>"
        return "<dhtk.templates.author.Author>"
