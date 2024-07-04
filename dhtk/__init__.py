# coding=utf-8
"""DHTK package entrypoint

Examples
    >>> d = start("WD", "corpus", gutenberg={"storage": "docker"})
    >>> melville = d.search("author", "Melville, Herman")
    >>> print(melville[0])
    {'author': 'Melville, Herman', 'aliases': 'Melville, Hermann', 'author_id': 'http://www.gutenberg.org/2009/agents/9'}
    >>> books_by_melville = d.get("author_id", melville[0]["author_id"])
    >>> d.corpus.add_works(books_by_melville)
    >>> d.corpus.print_works()
    0 Herman Melville Bartleby, the Scrivener: A Story of Wall-Street
    1 Herman Melville Battle-Pieces and Aspects of the War
    2 Herman Melville I and My Chimney
    3 Herman Melville I and My Chimney
    4 Herman Melville Index of the Project Gutenberg Works of Herman Melville
    5 Herman Melville Israel Potter: His Fifty Years of Exile
    6 Herman Melville John Marr and Other Poems
    7 Herman Melville Mardi: and A Voyage Thither, Vol. I
    8 Herman Melville Mardi: and A Voyage Thither, Vol. II
    9 Herman Melville Moby Dick
    10 Herman Melville Moby Dick; Or, The Whale
    11 Herman Melville Moby Dick; Or, The Whale
    12 Herman Melville Moby Dick; Or, The Whale
    13 Herman Melville Moby-Dick; or, The Whale
    14 Herman Melville Omoo: Adventures in the South Seas
    15 Herman Melville Omoo: Adventures in the South Seas
    16 Herman Melville Pierre; or The Ambiguities
    17 Herman Melville Redburn. His First Voyage Being the Sailor Boy Confessions and Reminiscences of the Son-Of-A-Gentleman in the Merchant Navy
    18 Herman Melville The Apple-Tree Table, and Other Sketches
    19 Herman Melville The Confidence-Man: His Masquerade
    20 Herman Melville The Piazza Tales
    21 Herman Melville Typee
    22 Herman Melville Typee
    23 Herman Melville Typee
    24 Herman Melville Typee: A Romance of the South Seas
    25 Herman Melville White Jacket; Or, The World on a Man-of-War

    >>> book = d.corpus[10]
    >>> book.print_info()
    Title       : Moby Dick; Or, The Whale
    Author      : Herman Melville
    Metadata    :
        - bookshelf   :
        - gutenberg_bookshelf: Best Books Ever Listings
        - gutenberg_creator: http://www.gutenberg.org/2009/agents/9
        - gutenberg_description: Project Gutenberg eBook #15 is believed to have the highest quality of the three editions of this eBook in the Project Gutenberg collection. #2701 and #2489 are the others. In addition, there is a computer-generated audio eBook, #9147, and a human audio performance, #28794.
        - gutenberg_downloads:          114
        - gutenberg_hasFormat:
                - https://www.gutenberg.org/cache/epub/2489/pg2489.cover.medium.jpg
                - https://www.gutenberg.org/cache/epub/2489/pg2489.cover.small.jpg
                - https://www.gutenberg.org/ebooks/2489.epub.images
                - https://www.gutenberg.org/ebooks/2489.epub.noimages
                - https://www.gutenberg.org/ebooks/2489.kindle.images
                - https://www.gutenberg.org/ebooks/2489.kindle.noimages
                - https://www.gutenberg.org/ebooks/2489.rdf
                - https://www.gutenberg.org/files/2489/2489-0.txt
                - https://www.gutenberg.org/files/2489/2489-0.zip
                - https://www.gutenberg.org/files/2489/2489-h.zip
                - https://www.gutenberg.org/files/2489/2489-h/2489-h.htm
                - https://www.gutenberg.org/files/2489/2489.txt
                - https://www.gutenberg.org/files/2489/2489.zip
        - gutenberg_id: http://www.gutenberg.org/ebooks/2489
        - gutenberg_issued:   2001-01-01
        - gutenberg_language:           en
        - gutenberg_license: http://www.gutenberg.org/license
        - gutenberg_media_type:         Text
        - gutenberg_publisher: Project Gutenberg
        - gutenberg_rights: Public domain in the USA.
        - gutenberg_subject:
                - Adventure stories
                - Ahab, Captain (Fictitious character) -- Fiction
                - Mentally ill -- Fiction
                - PS
                - Psychological fiction
                - Sea stories
                - Ship captains -- Fiction
                - Whales -- Fiction
                - Whaling -- Fiction
                - Whaling ships -- Fiction
        - gutenberg_title: Moby Dick; Or, The Whale
        - gutenberg_type:
                - http://www.gutenberg.org/2009/pgterms/ebook
                - http://www.w3.org/2002/07/owl#NamedIndividual
        - same_as     :
        - subject     :
    >>> book.get_data_file_name()
    '2489.txt'

"""
# Import dependencies

import logging
from dhtk.core import start, IS_INTERACTIVE, AVAILABLE_STORAGES, AVAILABLE_DATA_SOURCES

logger = logging
logger.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


# noinspection PyUnusedFunction
def print_usage_example() -> None:
    """
      Print a usage example.
    """
    print("Usage example: \n"
          "data_source = \"gutenberg\"\n"
          "storage = \"docker\"\n"
          "dhtk_client = dhtk.start(working_directory, data_source=datasource, storage=storage)\n"
          "dhtk_client.get(\"author\", \"all\")\n")


if IS_INTERACTIVE:
    print('\n'
          '##########################################################################################\n'
          'Welcome to the Digital Humanities ToolKit,\n'
          'the user-friendly Python API for \n'
          'Digital Humanities research.\n'
          '\n'
          'For more information, please visit DHTK\'s website:\n'
          '[https://dhtk.unil.ch/]\n'
          '\n'
          'Installed data_sources:\n'
          f'  {AVAILABLE_DATA_SOURCES}\n'
          f'Installed storages:\n'
          f'  {AVAILABLE_STORAGES}\n'
          '\n'
          'n.b. for usage example: dhtk.print_usage_example()\n'
          '##########################################################################################\n')
