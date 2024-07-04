# coding=utf-8
"""Contains the GutenbergData implementation of the abstract LiteraryData class"""

import logging
# Import dependencies
import re
import urllib
from typing import Dict

import typing
from SPARQLWrapper import SPARQLWrapper, JSON

from dhtk.data_sources.templates.data import Data
from .author import GutenbergAuthor
from .book import GutenbergBook

logger = logging.getLogger(__name__)


class GutenbergData(Data):
    """Class to searching the Gutenberg catalog using SPARQL queries,
    inheriting from the Abstract class LiteraryData (dhtk.data_sources.abstract_gutenberg)

    "Query" attributes participate to create a skeleton of a standard query :
        query_header + query_select + query_head.

    Args:

    Returns:


    """
    # TODO: implement different types than text! '?book_id dcterms:type dcmitype:Text.'
    # TODO: add method to search book when author is known.

    _namespace = "\n".join([
        "PREFIX dcterms: <http://purl.org/dc/terms/>",
        "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
        "PREFIX purl: <http://purl.org/dc/terms/>",
        "PREFIX owl: <http://www.w3.org/2002/07/owl#>",
        "PREFIX pgterms: <http://www.gutenberg.org/2009/pgterms/>",
        "PREFIX foaf: <http://xmlns.com/foaf/0.1/>",
        "PREFIX marcrel: <http://id.loc.gov/vocabulary/relators/>",
        "PREFIX dcmitype: <http://purl.org/dc/dcmitype/>",
        "PREFIX apf: <http://jena.apache.org/ARQ/property#>\n"
    ])

    _work_types = [
        "Text",
        "Image",
        "Sound",
        "Dataset",
        "StillImage",
        "Collection",
        "MovingImage",
    ]

    _book_metadata = ("<%s> rdf:type ?gutenberg_type .",
                      "<%s> pgterms:downloads ?gutenberg_downloads .",
                      "<%s> dcterms:publisher ?gutenberg_publisher .",
                      "<%s> dcterms:hasFormat ?gutenberg_hasFormat .",
                      """<%s> dcterms:language [rdf:value ?gutenberg_language] .""",
                      """<%s> dcterms:subject  [rdf:value ?gutenberg_subject] .""",
                      """<%s> dcterms:type [rdf:value ?gutenberg_media_type] .""",
                      "<%s> dcterms:rights ?gutenberg_rights .",
                      "<%s> dcterms:title ?gutenberg_title .",
                      "<%s> dcterms:issued ?gutenberg_issued .",
                      "<%s> dcterms:creator ?gutenberg_creator .",
                      "<%s> dcterms:license ?gutenberg_license .",
                      "<%s> dcterms:tableOfContents ?gutenberg_tableOfContents .",
                      "<%s> pgterms:marc010 ?gutenberg_marc010 .",
                      "<%s> pgterms:marc901 ?gutenberg_marc901 .",
                      """<%s> pgterms:bookshelf [rdf:value ?gutenberg_bookshelf] .""",
                      "<%s> pgterms:marc440 ?gutenberg_marc440 .",
                      "<%s> dcterms:description ?gutenberg_description .",
                      "<%s> marcrel:trl ?gutenberg_trl .",
                      "<%s> dcterms:alternative ?gutenberg_alternative .",
                      "<%s> foaf:isPrimaryTopicOf|owl:sameAs ?same_as",
                      "<%s> marcrel:edt ?gutenberg_edt .",
                      "<%s> marcrel:aui ?gutenberg_aui .",
                      "<%s> marcrel:pbl ?gutenberg_pbl .",
                      "<%s> marcrel:ill ?gutenberg_ill .",
                      "<%s> marcrel:cmm ?gutenberg_cmm .",
                      "<%s> marcrel:com ?gutenberg_com .",
                      "<%s> marcrel:oth ?gutenberg_oth .",
                      "<%s> pgterms:marc260 ?gutenberg_marc260 .",
                      "<%s> marcrel:ctb ?gutenberg_ctb .",
                      "<%s> marcrel:ann ?gutenberg_ann .",
                      "<%s> marcrel:egr ?gutenberg_egr .",
                      "<%s> pgterms:marc508 ?gutenberg_marc508 .",
                      "<%s> pgterms:marc546 ?gutenberg_marc546 .",
                      "<%s> pgterms:marc902 ?gutenberg_marc902 .",
                      "<%s> pgterms:marc520 ?gutenberg_marc520 .",
                      "<%s> pgterms:marc903 ?gutenberg_marc903 .",
                      "<%s> pgterms:marc300 ?gutenberg_marc300 .",
                      "<%s> marcrel:adp ?gutenberg_adp .",
                      "<%s> marcrel:pht ?gutenberg_pht .",
                      "<%s> marcrel:unk ?gutenberg_unk .",
                      "<%s> marcrel:prt ?gutenberg_prt .",
                      "<%s> marcrel:prf ?gutenberg_prf .",
                      "<%s> pgterms:marc250 ?gutenberg_marc250 .",
                      "<%s> pgterms:marc020 ?gutenberg_marc020 .",
                      "<%s> marcrel:cmp ?gutenberg_cmp .",
                      "<%s> marcrel:dub ?gutenberg_dub .",
                      "<%s> marcrel:arr ?gutenberg_arr .",
                      "<%s> marcrel:trc ?gutenberg_trc .",
                      "<%s> marcrel:clb ?gutenberg_clb .",
                      "<%s> marcrel:aft ?gutenberg_aft .",
                      "<%s> marcrel:res ?gutenberg_res .",
                      "<%s> marcrel:art ?gutenberg_art .",
                      "<%s> owl:sameAs|foaf:isPrimaryTopicOf ?same_as  .",)

    _author_metadata = ("<%s> pgterms:alias ?aliases .",
                        "<%s> pgterms:birthdate ?birth_date .",
                        "<%s> pgterms:deathdate ?death_date .",
                        "<%s> owl:sameAs|foaf:isPrimaryTopicOf ?same_as .",
                        "<%s> pgterms:webpage ?web_pages .",
                        # "<%s> rdf:type ?gutenberg_type .",
                        )

    def __init__(self, sparql_endpoint):
        """Initialize tools with the SPARQL endpoint,
        such as a local instance of the Apache Jena Fuseki server.

        Args:
            sparql_endpoint (str) : URL of the triplet store containing Gutenberg Catalog triplets.
        """
        self._search_cache = {}
        try:
            self._sparql_endpoint = SPARQLWrapper(sparql_endpoint)
        except Exception as error:
            raise EnvironmentError(
                f"Check the sparql_endpoint you provided!: {sparql_endpoint}"
            ) from error

        logger.info(
            "GUTENBERG: GutenbergData instantiated using SPARQL endpoint: %s", sparql_endpoint
        )

    # Bookshelves
    _shelves = """?book_id pgterms:bookshelf [dcterms:title ?bookshelf] ."""

    def all_bookshelves(self):
        """Return all bookshelves in the store.

        This method doesn't use the standard SPARQL query, but a specific to get only bookshelves.

        Returns:
            list : the results for the query

        """
        select = "SELECT DISTINCT ?bookshelf\n"
        pattern = f"WHERE {{\n\t{self._shelves}\n}}\nORDER BY ?bookshelf"
        query = self._namespace + select + pattern
        query = self._get_query_results(query)

        return [result["bookshelf"] for result in query]

    def search_by_bookshelf(self, bookshelf, works: bool = True):
        """Data in Gutenberg catalog all books corresponding to the given bookshelf string.

        The bookshelf is used as parameter in a SPARQL query.

        Args:
          bookshelf: bookshelf in plain text, case-insensitive. It can be a part of the bookshelf.
          works: boolean thant indicates if the function should return works.

        Returns:
            result of the query


        """
        logger.info(
            "GUTENBERG: Searching bookshelf: %s",
            bookshelf
        )
        select = "SELECT DISTINCT *"
        if works:
            select = "SELECT DISTINCT ?book_id"
        pattern = (
            "WHERE {\n"
            f"\t{self._shelves}"
            f'\tFILTER CONTAINS(lcase(str(?bookshelf)), "{bookshelf.lower()}")\n'
            f"\t{self._books}"
            "\tOPTIONAL {{ ?book_id dcterms:language [rdf:value ?language].}}\n"
            "}\n"
            "ORDER BY ?author ?author_id ?title ?book_id"
        )
        query = self._namespace + select + pattern
        results = self._get_query_results(query)
        if works:
            book_ids = list({result["book_id"] for result in results})
            return [self.get_book(book_id) for book_id in book_ids]
        return results

    # Subjects
    _subjects = (
        "\t?book_id dcterms:subject [rdf:value ?subjects].\n"
        '\t?subject apf:strSplit (?subjects " -- ")\n'
    )

    def all_subjects(self):
        """Return all subjects in the store.

        This method don't use the standard SPARQL query, but a specific to get only subjects.

        Returns:
            list : a list with the query results


        """
        select = "SELECT DISTINCT ?subject\n"
        pattern = (
            "WHERE {\n"
            f"{self._subjects}"
            "}\n"
            "ORDER BY ?subject"
        )
        query = self._namespace + select + pattern
        query = self._get_query_results(query)

        return [result["subject"] for result in query]

    def search_by_subject(self, subject, limit=0, works: bool = True):
        """Data in Gutenberg catalog all books with given subject string.

        The subject is used as parameter in a SPARQL query. If no limit value is specified,
        the method returns all books with the given subject.

        Args:
          subject(str): Subject in plain text, case-insensitive. It can be a part of the subject.
          limit(int, optional): Use to limit how many books are returned by the SPARQL query. (Default value = 0)
          works: boolean thant indicates if the function should return works.

        Returns:
            str : the query results


        """
        select = "SELECT DISTINCT *\n"
        if works:
            select = "SELECT DISTINCT ?book_id\n"
        pattern = (
            "WHERE {\n"
            f"{self._subjects}\n"
            f'FILTER CONTAINS(lcase(str(?subject)), "{subject.lower()}")\n'
            f'{self._books}'
            "\tOPTIONAL {{ ?book_id dcterms:language [rdf:value ?language].}}\n}\n"
            "ORDER BY ?author ?author_id ?title ?book_id"
        )
        query = self._namespace + select + pattern
        if limit > 0:
            query += f"LIMIT {limit}"

        results = self._get_query_results(query)
        if works:
            book_ids = list({result["book_id"] for result in results})
            return [self.get_book(book_id) for book_id in book_ids]
        return results

    # Authors
    _authors = "\t?author_id a pgterms:agent;\n\tpgterms:name ?author .\n"

    def all_authors(self):
        """Return all authors in the store.

        This method don't use the standard SPARQL query, but a specific to get only authors.

        Returns:
            list : the query results


        """
        select = "SELECT DISTINCT ?author ?author_id\n"
        pattern = (
            "WHERE {\n"
            f"{self._authors}"
            "}\nORDER BY ?author ?author_id"
        )
        query = self._namespace + select + pattern
        return {result["author"]: result["author_id"] for result in self._get_query_results(query)}

    def search_by_author(self, name: str, alias: str = None, works: bool = False):
        """
        Data books in the Gutenberg catalog by author's name and last name.
        The standard SPARQL query is overwritten by a sparql_filter and by a sort instruction.

        Args:
          name(str): Author's name, first name, last name or alias in plain text, case-insensitive.
                     It can be a part of the author's name. (Default value = None)
          alias:
          works: boolean thant indicates if the function should return works.
        Returns:
            the query results


        """

        # If alias is provided, looks for name AND alias
        # Otherwise assume the name might be an alias

        names = re.split(r'\W+', name)
        sparql_filter = ""
        for author_name in names:
            sparql_filter += f'\tFILTER (CONTAINS(lcase(str(?author)), "{author_name.lower()}")'
            if alias is None:
                sparql_filter += f' ||  CONTAINS(lcase(str(?aliases)), "{author_name.lower()}")'
            sparql_filter += ")\n"
        if alias is not None:
            aliases = re.split(r'\W+', alias)
            for author_alias in aliases:
                sparql_filter += f'\tFILTER (CONTAINS(lcase(str(?aliases)), "{author_alias.lower()}"))\n'

        select = "SELECT DISTINCT ?author ?aliases ?author_id\n"
        if works:
            select = "SELECT DISTINCT ?author_id\n"
        pattern = (
            "WHERE {\n"
            f"{self._authors}"
            f"{sparql_filter}"
            "\tOPTIONAL { ?author_id pgterms:alias ?aliases. }\n}\n"
            "ORDER BY ?author ?author_id"
        )

        query = self._namespace + select + pattern
        results = self._get_query_results(query)
        if works:
            author_ids = {result["author_id"] for result in results}
            results = []
            for author_id in author_ids:
                results.extend(list(self.get_bibliography(author_id, works=True)))
        return results

    def get_author(self, author_id: str, works: bool = True):
        """Create an author object with information collected from the Gutenberg Store.

        Args:
          author_id(str): The author identifier is a URI, like 'http://www.gutenberg.org/2009/agents/408'
          works: boolean thant indicates if the function should return works.

        Returns:
            str : the query results


        """
        select = "SELECT DISTINCT *\n"
        pattern = f"WHERE {{\n\t<{author_id}> pgterms:name ?name .\n}}"

        query = self._namespace + select + pattern
        query = self._get_query_results(query)[0]

        author = GutenbergAuthor(
            gutenberg_id=author_id,
            name=query["name"],
        )

        author.metadata.update(self.get_metadata(author))

        if works:
            return self.get_bibliography(author, works=True)
        return author

    def get_bibliography(self, author_id: typing.Union[str, GutenbergAuthor], works: bool = True):
        """To get all books written by an author.

        Args:
          author_id(str): The author identifier is a URI, like 'http://www.gutenberg.org/2009/agents/408'
          works: boolean thant indicates if the function should return works.

        Returns:
            list : the query results


        """
        author = None
        if isinstance(author_id, GutenbergAuthor):
            author = author_id
            author_id = author.get_gutenberg_id()
        elif isinstance(author_id, str):
            author = self.get_author(author_id, works=False)
        else:
            raise TypeError("author_id should be a string or a GutenbergAuthor")

        select = "SELECT DISTINCT ?title ?book_id\n"
        pattern = (
            "WHERE {\n"
            f"\t?book_id purl:creator <{author_id}>;\n"
            "\t\ta pgterms:ebook;\n"
            "\t\tpurl:title ?title.\n"
            f"\t<{author_id}> pgterms:name ?author.\n"
            "}\nORDER BY ?title ?book_id"
        )

        query = self._namespace + select + pattern
        results = [(result["title"], result["book_id"], author) for result in self._get_query_results(query)]
        if works:
            return tuple({self.get_book(result[1], result[2]) for result in results})
        return results

    # Books
    _books = f"\t?book_id a pgterms:ebook;\n\t\tpurl:title ?title.\n{_authors}"

    def all_books(self):
        """Return the title of all books in the store.

        This method don't use the standard query, but a specific to get only
        titles and book identifiers.

        Returns:
            list : the query results


        """
        select = "SELECT DISTINCT ?title ?author\n"
        pattern = (
            "WHERE {\n"
            f"{self._books}"
            "\n}\nORDER BY ?auhtor ?author_id ?title ?book_id"
        )
        query = self._namespace + select + pattern
        results = self._get_query_results(query)

        return [{"title": result['title'], "author": result['author']} for result in results]

    def search_by_title(self, title, works: bool = True):
        """Data in Gutenberg catalog all books with given title string.

        Args:
          title(str): Title in plain text, case-insensitive. It can be a part of the title.
          works: boolean thant indicates if the function should return works.

        Returns:
            str : the query results


        """
        select = "SELECT DISTINCT ?book_id ?title ?author_id ?author ?language\n"
        pattern = (
            "WHERE {\n"
            "\t?book_id a pgterms:ebook;\n" 
            "\t\tpurl:title ?title;\n"
            "\t\tpurl:creator ?author_id.\n"
            "\t?author_id pgterms:name ?author.\n"
            "\tOPTIONAL {?book_id dcterms:language [rdf:value ?language].}\n"
            f"\tFILTER CONTAINS(lcase(str(?title)), {repr(title).lower()})\n"
            "}\nORDER BY ?author ?author_id ?title ?book_id"
        )

        query = self._namespace + select + pattern
        results = self._get_query_results(query)
        if works:
            book_ids = list({result["book_id"] for result in results})
            return [self.get_book(book_id) for book_id in book_ids]
        return results

    def get_book(self, book_id: str, author: typing.Optional[GutenbergAuthor] = None, works: bool = True) -> GutenbergBook:
        """Create a book object with information collected from the Gutenberg Store.

        Args:
          book_id(str): The book identifier is a URI, like 'http://www.gutenberg.org/ebooks/20063'
          author:  (Default value = None)
          works:

        Returns:
            gutenberg.tools.book.Book :  A book object

        """

        select = "SELECT DISTINCT *\n"
        pattern = (
            "WHERE {\n"
            f"\t<{book_id}> purl:title ?title;\n" 
            "\t\tpurl:creator ?author_id;\n}"
        )
        if author:
            pattern = (
                "WHERE {\n"
                f"\tVALUES ?author_id {{ <{author.get_gutenberg_id()}>}}\n"
                f"\t<{book_id}> purl:title ?title;\n" 
                "\t\tpurl:creator ?author_id.\n}"
            )

        query = self._namespace + select + pattern
        book = self._get_query_results(query)
        if works and book:
            if not author:
                author = self.get_author(book[0]["author_id"], works=False)

            metadata = self.bookshelves_subjects(book_id)

            book = GutenbergBook(
                gutenberg_id=book_id,
                title=book[0]["title"],
                subject=metadata["subjects"] or None,
                bookshelf=metadata["bookshelves"] or None,
                author=author
            )
            metadata = self.get_metadata(book)
            book.metadata.update(metadata)
        return book

    def bookshelves_subjects(self, book_id: str) -> Dict[str, list]:
        """Return the bookshelves and the subjects of the given book,
        designated by his identifier.

        Args:
          book_id(str): A Gutenberg book identifier. Is a URI, like "http://www.gutenberg.org/ebooks/10053"

        Returns:
            dict : the query results with 'bookshelves' and 'subjects'


        """
        select = "SELECT DISTINCT ?subject ?bookshelf\n"
        pattern = (
            "WHERE {\n"
            f"\t<{book_id}> dcterms:subject [dcterms:title ?subject];\n"
            "\t\tpgterms:bookshelf [dcterms:title ?bookshelf].\n"
            "}\nORDER BY ?subject"
        )
        query = self._namespace + select + pattern
        results = self._get_query_results(query)

        subjects = list({result["subject"] for result in results})
        bookshelves = list({result["bookshelf"] for result in results})

        return {"bookshelves": bookshelves, "subjects": subjects}

    def query(self, query: str):
        """

        Args:
            query: a sparql query.

        Returns:
            list: The result of the query.
        """
        return self._get_query_results(query)

    def get_metadata(self, item):
        """Get metadata about the book that is present in the catalog.

        Args:
          item(An object having an entry "gutenberg_id" in the results of the method metadata().):
          The metadata of these tools must contain an entry called: "gutenberg_id"

        Returns:
            dict : the query results


        """

        query_results = self._metadata_query(item)

        metadata = {}
        if len(query_results) == 1:
            metadata = query_results[0]
        else:
            for key in query_results[0]:
                values = list({row[key] for row in query_results})
                if len(values) == 1:
                    metadata[key] = values.pop()
                else:
                    metadata[key] = sorted(values)
        return metadata

    def _metadata_query(self, item: typing.Union[GutenbergAuthor, GutenbergBook]):
        """Helper function to get metadata for different item types.

        Args:
          item(An object having an entry "gutenberg_id" in the results of the method metadata().):
          The metadata of these tools must contain an entry called: "gutenberg_id"

        Returns:
            list : the query results

        TODO: fix this! One query should be sufficent.
        """
        query = self._namespace
        query += "SELECT DISTINCT *\nWHERE {\n"

        if isinstance(item, GutenbergBook):
            book_id = item.get_book_id()
            for metadata in self._book_metadata:
                query += "\tOPTIONAL { " + metadata % book_id + " }\n"
        elif isinstance(item, GutenbergAuthor):
            author_id = item.get_gutenberg_id()
            for metadata in self._author_metadata:
                query += "\tOPTIONAL { " + metadata % author_id + "} \n"
        query += "\n}"
        return self._get_query_results(query)

    # Queries
    def _get_query_results(self, query):
        """Use a SPARQL query to get results from the triplet store.

        Args:
          query(str): A structured string in the SPARQL language used to ask the triplet store.

        Returns:
            list : the query results


        """
        logger.debug(
            "GUTENBERG: Executing query:\n\n%s\n",
            query
        )

        sparql = self._sparql_endpoint

        sparql.setQuery(query)
        logger.debug(query)
        sparql.setReturnFormat(JSON)
        try:
            query_results = sparql.queryAndConvert()
        except urllib.error.HTTPError:
            return None
        results = []
        for entry in query_results["results"]["bindings"]:
            formatted_entry = {}
            for key, value in entry.items():
                formatted_entry[key] = value["value"]
            results.append(formatted_entry)
        return results

    def statistics(self):
        """Print information about the Gutenberg catalog.

        Args:

        Returns:
          str: Formatted string of different statistics. Subject counts sub-subjects too.

        Notes:
            This method is relatively slow due to the fact that it inspects the whole Gutenberg RDF.

        Examples:

            >>> self.statistics()
            # number of books        :     60101
            # number of authors      :     20908
            # number of bookshelves  :       335
            # number of subjects     :     17524
        """
        statistics = {}

        query = (
            "PREFIX pgterms: <http://www.gutenberg.org/2009/pgterms/>\n"
            "SELECT (COUNT(DISTINCT ?book) as ?total)\n"
            "WHERE { ?book a pgterms:ebook . }\n"
        )
        statistics["number_of_books"] = self._get_query_results(query)[0]["total"]

        query = (
            "PREFIX pgterms: <http://www.gutenberg.org/2009/pgterms/>\n"
            "SELECT (COUNT(DISTINCT ?author) as ?total)\n"
            "WHERE { ?author a pgterms:agent . }\n"
        )
        statistics["number_of_authors"] = self._get_query_results(query)[0]["total"]

        query = (
            "PREFIX pgterms: <http://www.gutenberg.org/2009/pgterms/>\n"
            "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
            "SELECT (COUNT(DISTINCT ?bookshelf) as ?total)\n"
            "WHERE { ?_ pgterms:bookshelf [rdf:value ?bookshelf] . }"
        )
        statistics["number_of_bookshelves"] = self._get_query_results(query)[0]["total"]

        query = (
            "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
            "PREFIX dcterms: <http://purl.org/dc/terms/>\n"
            "PREFIX apf: <http://jena.apache.org/ARQ/property#>\n"
            "SELECT (COUNT(DISTINCT ?subject) as ?total)\n"
            "WHERE {\n"
            "\t?_ dcterms:subject [rdf:value ?subjects].\n"
            '\t?subject apf:strSplit (?subjects " -- ")\n'
            "}"
        )
        statistics["number_of_subjects"] = self._get_query_results(query)[0]["total"]
        text = ""
        for key, value in statistics.items():
            text += f"\n{key.replace('_', ' '):23}:\t {value:>5}"

        return text
