# coding=utf-8
"""Contains the GutenbergAuthor Class."""

import copy
import re
import logging
from nameparser import HumanName
from nameparser.config.titles import FIRST_NAME_TITLES

from dhtk.corpus.author import Author

logger = logging.getLogger(__name__)


class GutenbergAuthor(Author):
    """The class for an author extended with variables from the gutenberg project.
    Child of the generic Author class.

    Example
    --------

        from pprint import pprint
        from  dhtk.data_sources.gutenberg.api.author import GutenbergAuthor

        # Create an author manually.
        adam_smith_author = GutenbergAuthor(
            gutenberg_id='http://www.gutenberg.org/2009/agents/1158',
            name='Smith, Adam'
        )

        # create an author form the gutenberg repository

        from dhtk.data_sources.gutenberg.data import GutenbergData

        database = GutenbergData()
        database.search_author_by_name("Adam", "Smith")
        # [('Smith, Adam', 'http://www.gutenberg.org/2009/agents/1158'),
        #  ('Smith, George Adam', 'http://www.gutenberg.org/2009/agents/5016')]

        adam_smith_author_pg = database.author_from_author_id(
            'http://www.gutenberg.org/2009/agents/1158'
        )

        adam_smith_author_pg.print_info()
        # Adam Smith
        # Metadata    :
        #     - gutenberg_id: http://www.gutenberg.org/2009/agents/1158
        #     - id          : http://www.gutenberg.org/2009/agents/1158
        #     - gutenberg_name:  Smith, Adam
        #     - gutenberg_aliases:
        #     - aliases     :
        #     - web_pages   :
        #             - http://en.wikipedia.org/wiki/Adam_Smith
        #     - birth_date  :         1723
        #     - death_date  :         1790

    Args:

    Returns:

    Args:

    Returns:


    """

    def __init__(self, gutenberg_id, name, aliases=None, web_pages=None, same_as=None, **kwargs):
        """
        Init function of GutenbergAuthor.

        Notes:
            Implement the Abstract Author class and extend it with the gutenberg id, the eventual alias(es) and the
            eventual web page(s) of the author. Converts name into a HumanName object with convert_name.

        Parameters:
            gutenberg_id (str) : URI of the gutenberg author in the Gutenberg RDF.
            name (str) : Name of the author.
            aliases set(str):   Eventual aliases of the author (default None).
            web_pages set(str):  Eventual web pages of the author (default None).

        """
        Author.__init__(
            self,
            name,
            metadata={},
        )
        metadata = {}
        if same_as is None:
            same_as = {}
        metadata["same_as"] = same_as
        id_format = re.compile(r"http://www.gutenberg.org/2009/agents/\d+$")
        if not id_format.fullmatch(gutenberg_id):
            raise ReferenceError(f"This gutenberg id is not valid: {gutenberg_id}")
        metadata["gutenberg_id"] = gutenberg_id
        metadata["id"] = gutenberg_id

        metadata["gutenberg_name"] = name

        if not isinstance(aliases, set):
            aliases = set()
        metadata["aliases"] = aliases

        if not isinstance(web_pages, set):
            web_pages = set()
        metadata["web_pages"] = web_pages

        # Add saint to nameparser's FIRST_NAME_TITLES
        FIRST_NAME_TITLES.add("saint")
        name = self.convert_name(name)

        # LOGGER.debug("converting aliases names: %s", ", ".join(aliases))
        metadata["aliases"] = [str(self.convert_name(alias)) for alias in aliases if alias]
        # LOGGER.debug("aliases: %s", ", ".join(self.metadata["aliases"]))

        if str(name) in metadata["aliases"]:
            # LOGGER.debug("removing '%s' from %s", str(name), ", ".join(self.metadata["aliases"]))
            metadata["aliases"].remove(str(name))

        self.metadata.update(metadata)

    def convert_name(self, human_name):
        """Convert human_name string containing into a HumanName object.

       Args:
          human_name(str): Author's name in a string.

        Returns:


        Notes:
            Is done in the init for every GutenbergAuthor object with initial string parameter "name".
        """

        human_name = HumanName(human_name)
        if human_name.suffix:
            self.metadata.update({"gutenberg_name_suffix": human_name.suffix})
            human_name.suffix = ""
        if human_name.nickname:
            # LOGGER.debug("%s nickname: %s", str(human_name), human_name.nickname)
            no_nickname = copy.copy(human_name)
            no_nickname.nickname = ""
            first_name_match = re.match(
                re.sub(r"(([A-Z])[a-z]*[.])", r"\2\\w+", human_name.first, re.UNICODE),
                human_name.nickname,
                re.UNICODE
            )
            logger.debug(
                "%s, %s",
                re.sub(
                    r"(([A-Z])[a-z]*[.])", r"\2\\w+",
                    human_name.first,
                    re.UNICODE
                ),
                human_name.nickname
            )
            if first_name_match and len(first_name_match.group(0)) >= len(human_name.first):
                human_name.first = first_name_match.group(0)
                human_name.nickname = human_name.nickname[len(human_name.first):].strip()
                # LOGGER.debug("Adding %s to aliases", str(no_nickname))
                self.metadata.update({"aliases": str(no_nickname)})
            middle_name_match = re.match(
                re.sub(r"(([A-Z])[a-z]*[.])", r"\2\\w+", human_name.middle, re.UNICODE),
                human_name.nickname,
                re.UNICODE
            )
            logger.debug(
                "%s, %s",
                re.sub(
                    r"(([A-Z])[a-z]*[.])", r"\2\\w+",
                    human_name.middle, re.UNICODE
                ),
                human_name.nickname
            )
            if middle_name_match and len(middle_name_match.group(0)) >= len(human_name.middle):
                human_name.middle = middle_name_match.group(0)
                human_name.nickname = human_name.nickname[len(human_name.middle):].strip()
                # LOGGER.debug("Adding %s to aliases", str(no_nickname))
                self.metadata.update({"aliases": str(no_nickname)})
        return human_name

    def get_gutenberg_id(self):
        """
        Get the gutenberg id url of the author.

        Returns:
            str: the guteneberg id

        """
        return self.metadata.get("gutenberg_id", "")

    def __eq__(self, other):
        """
        Equality function between authors.

        Notes:
            Test the equality of the two authors. Using the gutenberg_id if other is an instance of
            GutenbergAuthor. If not, it uses the dhtk.common.author.Author.__eq__() method that uses the
            author's names (first, last) and its birthdate.

        Args:
            other (dhtk.data_sources.templates.author.Author): An instance of dhtk.common.author.Author or
            of its child-classes.

        Returns:
            equality (bool) : A bool that tells if the authors are the same or not.

        """
        if isinstance(other, GutenbergAuthor):
            equals = self.get_gutenberg_id() == other.get_gutenberg_id()
        else:
            equals = super().__eq__(other)
        return equals

    def __hash__(self):
        """
        Return hash for the author.

        Returns:
            hash (int) : The hash value for the author.
        """
        return hash((self.get_first_name() + self.get_last_name() + self.get_birth_date()))

    def __repr__(self):
        """

        Returns:
            object_str (str) : String representing the object
        """

        return f"<Author: {self.get_last_name()}, {self.get_first_name()}" \
               f"({self.get_gutenberg_id()}>)"
