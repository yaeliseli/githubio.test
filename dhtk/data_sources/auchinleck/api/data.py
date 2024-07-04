from SPARQLWrapper import SPARQLWrapper, JSON
import urllib.parse
import re

import logging

logger = logging.getLogger(__name__)


class AuchinleckData:
    """
    Class to searching the Auchinleck Lexicon using SPARQL queries
    """

    _namespace = """
    PREFIX auch: <http://www.semanticweb.org/cyrille/ontologies/2020/7/untitled-ontology-18#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX lemon: <http://lemon-model.net/lemon#>
    """

    _regex_str = r"http://www\.semanticweb\.org/cyrille/ontologies/2020/7/untitled-ontology-18#"

    def __init__(self, sparql_endpoint="http://dhtk.unil.ch/auchinleck/sparql"):
        """
        Initialize objects with the SPARQL endpoint, such as a local instance of the Apache Jena Fuseki server.

        Parameters
        ----------
        sparql_endpoint: str
            URL of the triplet store containing Gutenberg Catalog triplets.
        """
        self._sparql_endpoint = SPARQLWrapper(sparql_endpoint)
        logger.info(f"AUCHINLECK: AuchinleckData instantiated using SPARQL endpoint: {sparql_endpoint}")

    def get_custom_query(self, custom_sparql_query, desired_variables):
        """
        Allow the user to perform a custom query

        Parameters
        ----------
        custom_sparql_query: str
            SPARQL query proposed by the user
        desired_variables: list
            name of the variables the custom query will return

        Returns
        -------
        results_list: list
            list of results of desired variables
            (list of dict: [{var1: 'var1a', var2: 'var2a', ...}, {var1: 'var1b', var2: 'var2b', ...}, ...])

        """
        results_list = list()

        query = self._namespace + custom_sparql_query

        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            row_dict = dict()
            for variable in desired_variables:
                # convert URIRef object to string
                variable_iri = result[variable]['value']
                # strip the auchinleck namespace off the string
                striped_variable = re.sub(self._regex_str, '', variable_iri)
                # replace escape characters of the URL
                decoded_variable = urllib.parse.unquote_plus(striped_variable)
                # add variable to dict
                row_dict[variable] = decoded_variable

            results_list.append(row_dict)

        return results_list

    def get_french_words(self):
        """
        Get all the French-based lexicon words

        Returns
        -------
        results_list : list
            list of dict with keys lexicon_word and etymology

        """

        pattern = """
            SELECT ?etymology ?id ?lexicon_word
            WHERE {
              ?etymology rdf:type auch:FrenchEtymology .
              ?id auch:hasEtymology ?etymology .
              ?id auch:isIDOf ?lexicon_word
            }
        """

        query = self._namespace + pattern

        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        results_list = list()
        for result in results['results']['bindings']:
            # convert URIRef object to string
            word_uri = result['lexicon_word']['value']
            # strip the Namespace off the string
            striped_word = re.sub(self._regex_str, '', word_uri)
            # replace escape characters of the URL
            decoded_word = urllib.parse.unquote_plus(striped_word)
            results_list.append({'lexicon_word': decoded_word, 'etymology': 'french'})

        return results_list

    def get_english_words(self):
        """
        Get all the English-based lexicon words

        Returns
        -------
        results_list : list
            list of dict with keys lexicon_word and etymology
        """

        results_list = list()

        pattern = """
            SELECT ?etymology ?id ?lexicon_word
            WHERE {
              ?etymology rdf:type auch:EnglishEtymology .
              ?id auch:hasEtymology ?etymology .
              ?id auch:isIDOf ?lexicon_word
            }
            """

        query = self._namespace + pattern

        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            # convert URIRef object to string
            word_uri = result['lexicon_word']['value']
            # strip the Namespace off the string
            striped_word = re.sub(self._regex_str, '', word_uri)
            # replace escape characters of the URL
            decoded_word = urllib.parse.unquote_plus(striped_word)
            results_list.append({'lexicon_word': decoded_word, 'etymology': 'english'})

        return results_list

    def get_latin_words(self):
        """
        Get all the Latin-based lexicon words

        Returns
        -------
        results_list: list
            list of dict with keys lexicon_word and etymology
        """

        results_list = list()

        pattern = """
            SELECT ?etymology ?id ?lexicon_word
            WHERE {
              ?etymology rdf:type auch:LatinEtymology .
              ?id auch:hasEtymology ?etymology .
              ?id auch:isIDOf ?lexicon_word
            }
            """

        query = self._namespace + pattern

        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            # convert URIRef object to string
            word_uri = result['lexicon_word']['value']
            # strip the Namespace off the string
            striped_word = re.sub(self._regex_str, '', word_uri)
            # replace escape characters of the URL
            decoded_word = urllib.parse.unquote_plus(striped_word)
            results_list.append({'lexicon_word': decoded_word, 'etymology': 'latin'})

        return results_list

    def get_scandinavian_words(self):
        """
        Get all the Scandinavian-based lexicon words

        Returns
        -------
        results_list: list
            list of dict with keys lexicon_word and etymology
        """

        results_list = list()

        pattern = """
            SELECT ?etymology ?id ?lexicon_word
            WHERE {
              ?etymology rdf:type auch:ScandinavianEtymology .
              ?id auch:hasEtymology ?etymology .
              ?id auch:isIDOf ?lexicon_word
            }
            """

        query = self._namespace + pattern

        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            # convert URIRef object to string
            word_uri = result['lexicon_word']['value']
            # strip the Namespace off the string
            striped_word = re.sub(self._regex_str, '', word_uri)
            # replace escape characters of the URL
            decoded_word = urllib.parse.unquote_plus(striped_word)
            results_list.append({'lexicon_word': decoded_word, 'etymology': 'scandinavian'})

        return results_list

    def get_other_words(self):
        """
        Get all the lexicon words with another etymology

        Returns
        -------
        results_list: list
           list of dict with keys lexicon_word and etymology
        """

        results_list = list()

        pattern = """
            SELECT ?etymology ?id ?lexicon_word
            WHERE {
              ?etymology rdf:type auch:OtherEtymology .
              ?id auch:hasEtymology ?etymology .
              ?id auch:isIDOf ?lexicon_word
            }
            """

        query = self._namespace + pattern

        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            # convert URIRef object to string
            word_uri = result['lexicon_word']['value']
            # strip the Namespace off the string
            striped_word = re.sub(self._regex_str, '', word_uri)
            # replace escape characters of the URL
            decoded_word = urllib.parse.unquote_plus(striped_word)
            results_list.append({'lexicon_word': decoded_word, 'etymology': 'other'})

        return results_list

    def get_unknown_words(self):
        """
        Get all the lexicon words with unknown etymology

        Returns
        -------
        results_list: list
            list of dict with keys lexicon_word and etymology
        """

        results_list = list()

        pattern = """
            SELECT ?etymology ?id ?lexicon_word
            WHERE {
              ?etymology rdf:type auch:UnknownEtymology .
              ?id auch:hasEtymology ?etymology .
              ?id auch:isIDOf ?lexicon_word
            }
            """

        query = self._namespace + pattern

        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            # convert URIRef object to string
            word_uri = result['lexicon_word']['value']
            # strip the Namespace off the string
            striped_word = re.sub(self._regex_str, '', word_uri)
            # replace escape characters of the URL
            decoded_word = urllib.parse.unquote_plus(striped_word)
            results_list.append({'lexicon_word': decoded_word, 'etymology': 'unknown'})

        return results_list

    def get_composition_year(self, lexicon_word):
        """
        Get the composition year of a specified word

        Parameters
        ----------
        lexicon_word: str
            a word in the lexicon

        Returns
        -------
            result_list: list
                list of single dictionary with keys 'lexicon_word', 'composition_year_min' and 'composition_year_max'

        """

        result_list = list()

        # replace special characters in string
        lexicon_word_encoded = urllib.parse.quote_plus(lexicon_word)

        pattern = """
            SELECT ?id ?year_min ?year_max ?lexicon_word
            WHERE {
              ?id auch:isIDOf auch:%s .
              ?id auch:hasCompositionYearMin ?year_min .
              ?id auch:hasCompositionYearMax ?year_max .
            }
            """ % lexicon_word_encoded

        query = self._namespace + pattern

        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            # convert URIRef object to string
            year_min_uri = result['year_min']['value']
            year_max_uri = result['year_max']['value']
            # strip the Namespace off the string
            striped_year_min = re.sub(self._regex_str, '', year_min_uri)
            striped_year_max = re.sub(self._regex_str, '', year_max_uri)

            result_list = [{
                'lexicon_word': lexicon_word,
                'composition_year_min': striped_year_min,
                'composition_year_max': striped_year_max,
            }]

        return result_list

    def get_manuscript_year(self, lexicon_word):
        """
        Get the minimum and maximum manuscript years of a specified word

        Parameters
        ----------
        lexicon_word: str
            a word in the lexicon

        Returns
        -------
        results_list: list
            list of single dictionary with keys 'lexicon_word', 'manuscript_year_min' and 'manuscript_year_max'


        """

        result_list = list()

        # replace special characters in string
        lexicon_word_encoded = urllib.parse.quote_plus(lexicon_word)

        pattern = """
            SELECT ?id ?year_min ?year_max ?lexicon_word
            WHERE {
              ?id auch:isIDOf auch:%s .
              ?id auch:hasManuscriptYearMin ?year_min .
              ?id auch:hasManuscriptYearMax ?year_max .
            }
            """ % lexicon_word_encoded

        query = self._namespace + pattern

        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            # convert URIRef object to string
            year_min_uri = result['year_min']['value']
            year_max_uri = result['year_max']['value']
            # strip the Namespace off the string
            striped_year_min = re.sub(self._regex_str, '', year_min_uri)
            striped_year_max = re.sub(self._regex_str, '', year_max_uri)

            result_list = [{
                'lexicon_word': lexicon_word,
                'manuscript_year_min': striped_year_min,
                'manuscript_year_max': striped_year_max,
            }]

        return result_list

    def get_dictionary_form(self, lexicon_word):
        """
        Get the unique dictionary (canonical) form of a specified lexicon word

        Parameters
        ----------
        lexicon_word: str
            a word in the lexicon

        Returns
        -------
        result_list : list
            list of single dictionary with keys 'lexicon_word' and 'dictionary_word'


        """

        result_list = list()

        # replace special characters in string
        lexicon_word_encoded = urllib.parse.quote_plus(lexicon_word)

        pattern = """
            SELECT ?id ?dictionary_word ?lexicon_word
            WHERE {
              ?id auch:isIDOf auch:%s .
              ?id auch:hasDictionaryWord ?dictionary_word .
            }
            """ % lexicon_word_encoded

        query = self._namespace + pattern

        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            # convert URIRef object to string
            word_uri = result['dictionary_word']['value']
            # strip the Namespace off the string
            striped_word = re.sub(self._regex_str, '', word_uri)
            # replace escape characters of the URL
            decoded_word = urllib.parse.unquote_plus(striped_word)
            result_list = [{
                'lexicon_word': lexicon_word,
                'dictionary_word': decoded_word,
            }]

        return result_list

    def get_poem_lexicon(self, poem_title):
        """
        Get the lexicon of a specific poem

        Parameters
        ----------
        poem_title: str
            the title of an Auchinleck poem

        Returns
        -------
        result_list: list
            list of the lexicon words in the poem

        """

        result_list = list()

        poem_title_encoded = urllib.parse.quote(poem_title)

        pattern = """
            SELECT ?lexicon_word
            WHERE {
              ?lexicon_word auch:existsIn auch:%s
            }
            """ % poem_title_encoded

        query = self._namespace + pattern

        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            # convert URIRef object to string
            word_uri = result['lexicon_word']['value']
            # strip the Namespace off the string
            striped_word = re.sub(self._regex_str, '', word_uri)
            # replace escape characters of the URL
            decoded_word = urllib.parse.unquote(striped_word)
            result_list.append({'lexicon_word': decoded_word, 'poem': poem_title})

        return result_list

    def get_etymology_stats(self, etymology_uri):
        """
        Get the number of words of a specific etymology in the dataset

        Parameters
        ----------
        etymology_uri : the URI of an etymology
        Etymologies URI are:
        - 'french_etymology'
        - 'english_etymology'
        - 'latin_etymology'
        - 'scandinavian_etymology'
        - 'unknown_etymology'
        - 'other_etymology'

        Returns
        -------
        A string with the etymology and its number of words in the dataset

        Example
        _______
        ::

        'french_etymology : 4051'

        """

        nbr_words = ""

        pattern = """
            SELECT (COUNT(*) AS ?count)
            WHERE{
                ?word rdf:type lemon:LexicalEntry .
                ?word auch:hasID ?id .
                ?id auch:hasEtymology auch:%s
            }
        """ % etymology_uri

        query = self._namespace + pattern
        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            nbr_words = result['count']['value']

        etymology_stats_str = "\n" + etymology_uri + ":" + str(nbr_words)

        return etymology_stats_str

    def statistics(self):
        """
        Get basic statistics about the dataset (the number of words in total and by etymology)

        Returns
        -------
        A string with the total number of words and the number of words by etymology.

        Example
        _______
        ::

        'total words : 14846
        french_etymology : 4051
        english_etymology : 7855
        ...'

        """

        stats_str = ""
        nbr_lexicon_words = ""

        pattern = """
            SELECT (COUNT(*) AS ?count)
            WHERE{
                ?word rdf:type lemon:LexicalEntry .
            }
        """

        query = self._namespace + pattern
        sparql = self._sparql_endpoint
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            nbr_lexicon_words = result['count']['value']

        stats_str += "\ntotal words: " + str(nbr_lexicon_words)
        stats_str += self.get_etymology_stats('french_etymology')
        stats_str += self.get_etymology_stats('english_etymology')
        stats_str += self.get_etymology_stats('latin_etymology')
        stats_str += self.get_etymology_stats('scandinavian_etymology')
        stats_str += self.get_etymology_stats('other_etymology')
        stats_str += self.get_etymology_stats('unknown_etymology')

        return stats_str
