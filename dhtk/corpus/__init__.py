# coding=utf-8
# coding=utf-8

"""Contains the class for creating a corpus."""
import pathlib
import shutil

import logging
from typing import Dict, Optional, List
import warnings

from .work import Work

logger = logging.getLogger(__name__)
warnings.formatwarning = lambda message, *args: f"{message}\n"


# noinspection PyUnusedFunction
class Corpus:
    """
    Create a corpus form dhtk works

    Examples
    >>> Corpus("corpus", "WD/corpora")
    """

    def __init__(
            self,
            name: str,
            corpora_path:
            str,
            description: str = "",
            work_list: Optional[List[Work]] = None
    ) -> None:
        """

        Args:
            name : str
                Name of the corpus.
            description : str
                A description of the corpus.
            corpora_path : str
                Path where the texts of the books in the corpus are saved.
            work_list : list(dhtk.corpus.work.Work)
                A list of templates.book.Book and/or child objects of it.
        """
        self.name = name
        self._description = description
        self.__work_list = []
        # If there is a list of books, add the current_work to the list.
        if work_list:
            self.add_works(work_list)
        # If any path exist, ask for a directory and create one.
        try:
            if not corpora_path:
                corpora_path = input("Choose a directory path to save your corpora:")
            elif isinstance(corpora_path, str):
                corpora_path = pathlib.Path(corpora_path)
            self.__corpora_path = corpora_path
            corpora_path.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise OSError("Can not find or create corpora path") from error
        self.__work_list.sort()

    def set_name(self, name: str) -> str:
        """

        Args:
            name: The new name of the corpus.

        Returns:

        """
        if name == self.name:
            return name
        old_path = pathlib.Path(self.get_corpus_path())
        new_path = self.__corpora_path / name
        if new_path.exists():
            warnings.warn(
                f"can't change name: the corpus already exists: {new_path.name}"
            )
            return self.name
        if old_path.exists():
            try:
                shutil.move(old_path, new_path)
            except OSError as error:
                raise OSError(
                    f"Could not move : {old_path.name} to {new_path.name}"
                ) from error
            self.name = name
        else:
            new_path.mkdir(parents=True, exist_ok=True)
        return name

    def get_corpus_path(self) -> pathlib.Path:
        """Return the path containing the current_work files of the works in the corpus.

        Args:

        Returns:
          str: Path of corpus with the name of directory and the name of corpus.
          Example:
          -------:
          :: corpus.get_corpus_path()
          # '~Desktop/jane_austen'

        Raises:


        """
        return self.__corpora_path / self.name

    def get_name(self):
        """Return the name of the corpus.

        Args:

        Returns:
          str: The corpus file will be saved in the local machine with this name.
          Example:
          -------: corpus.get_name()
          # 'jane_austen'

        Raises:


        """
        return self.name

    def get_description(self):
        """Return the description of the corpus.

        Returns:
          str: The description of the corpus
      Example:
          >>>  corpus = Corpus("corpus", "WD/corpora")
          ... corpus.get_description()
          # 'Books by Jane Austen'

        """

        return self._description

    def get_works(self):
        """Return the list of works in the corpus.

        Returns:
          list(dhtk.templates.book.Book): Books in the corpus

        Example:
            >>> from pprint import pprint
            ... corpus = Corpus("corpus", "WD/corpora")
            ... pprint(corpus.get_works())
            $ [<GutenbergBook: Jane Austen - Emma gutenberg_id: 158>,
            $ <GutenbergBook: Jane Austen - Gevoel en verstand gutenberg_id: 25946>,
            $ <GutenbergBook: Jane Austen - Emma gutenberg_id: 19839>,
            $ <GutenbergBook: Jane Austen - Lady Susan gutenberg_id: 22953>]

        """
        return sorted(self.__work_list)

    def print_works(self):
        """Print list of books in the corpus.

        This list containing the number of works in corpus, authors' full name and the books title.

        Example:
            Create a corpus by the author named Ashford Daisy

            >>>  corpus = Corpus("corpus", "WD/corpora")
            ... corpus.print_works()
            # 0 Jane Austen Emma
            # 1 Jane Austen Gevoel en verstand
            # 2 Jane Austen Emma
            # 3 Jane Austen Lady Susan


        """
        for index, current_work in enumerate(self.__work_list):
            author = current_work.get_author()
            author_full_name = author.get_name()
            work_title = current_work.get_title()
            print(f"{index} {author_full_name} {work_title}")

    def add_work(self, current_work):
        """Add a single work to the corpus.

        Args:
          current_work: The work to add.

        Returns:

        Raises:


        """
        # If the object is a current_work, add it to the corpus that already exist.
        if current_work not in self.__work_list:
            if isinstance(current_work, Work):
                self.__work_list.append(current_work)
            else:
                raise TypeError(
                    "It is only possible to add works of type Work to the corpus"
                )
        self.__work_list.sort()

    def add_works(self, works_list):
        """Add a list of books to the corpus.

        Args:
          works_list(list(dhtk.templates.book.Book)): A list of books form current_work id.
        This list can get form searching in gutenberg
        and get the list of books id  using the method `book_from_book_id()`
        from :class: `GutenbergData`
        in order to add to the corpus that already exist.
        Each current_work of in the new list will be added by the method of `add_book()`

        Returns:

        Raises:


        """
        for current_work in works_list:
            self.add_work(current_work)
        self.__work_list.sort()

    def get_work_data_file_name(self, current_work):
        """Return a good filename for a book.

        Args:
          current_work(dhtk.templates.book.Book): It is the current_work from searching in gutenberg
        and get current_work id using the method `book_from_book_id()`.

        Returns:
          str: This method return to the method in Book of type `dhtk.templates.current_work` which get the name
          of author and the titre of the current_work, separate each word by adding '_' to create
          a filename of a single book. Or the id of the current_work followed by the name of its source.
          At the end of current_work's filename, the suffix of .txt
          will be also added.
          Example:
          -------:
          :: corpus.get_text_file_name(corpus[1])
          # '25946-gutenberg.txt'

        Raises:


        """
        result = None
        if current_work in self.__work_list:
            result = current_work.get_data_file_name()
        elif isinstance(current_work, int) and 0 <= current_work < len(self.__work_list):
            result = self.__work_list[current_work].get_data_file_name()
        return result

    def remove_work(self, current_work):
        """Delete a current_work form the corpus by deleting the current_work form list of books and also the file of
        current_work in the local
        machine.

        Args:
          current_work(dhtk.templates.book.Book): The current_work to remove from the corpus

        Returns:

        Raises:


        """
        if current_work in self.__work_list:
            self.__work_list.remove(current_work)
        elif isinstance(current_work, int) and 0 <= current_work < len(self.__work_list):
            del self.__work_list[current_work]
        else:
            raise IndexError(
                f"Could not find the current_work you are trying to remove : {current_work}"
            )

        file_path = self.get_corpus_path() / self.get_work_data_file_name(current_work)
        if file_path.exists():
            file_path.unlink()

    def get_info(self):
        """

        Returns: a short description of the class.

        """
        return (
            f"Name: {self.name}\n"
            f"Description: {self._description}\n"
            f"Path:        {self.get_corpus_path()}\n"
            f"# of works:  {len(self.__work_list)}\n"
        )

    def clear(self):
        """Delete all files and books in the corpus."""
        folder = self.get_corpus_path()
        for file_path in folder.glob("*.*"):
            file_path.unlink()
        folder.rmdir()
        self.__work_list.clear()

    def download_work(self, current_work):
        """Download the text file for a single book.

        Args:
          current_work(dhtk.templates.book.Book):

        Returns:

        Raises:


        """
        corpus_path = self.get_corpus_path()
        corpus_path.mkdir(parents=True, exist_ok=True)
        if current_work in self.__work_list:
            current_work.save_data_file_to(corpus_path)
        elif isinstance(current_work, int) and 0 <= current_work < len(self.__work_list):
            self.__work_list[current_work].save_data_file_to(corpus_path)
        else:
            logger.info("File %s already exists in %s.", current_work.get_data_file_name(), corpus_path)

    def download_corpus_data_files(self):
        """Download the text files for the full corpus to the corpus path directory.

        Example
        -------
        ::

            corpus.download_book_corpus()
            pprint(os.listdir(corpus.get_corpus_path()))
            # ['158-gutenberg.txt',
            #  '19839-gutenberg.txt',
            # '121-gutenberg.txt',
            # '22954-gutenberg.txt',
            # '1212-gutenberg.txt',
            # '25946-gutenberg.txt',
            # '22962-gutenberg.txt',
            # '22953-gutenberg.txt']

        Args:

        Returns:

        Raises:

        """
        corpus_path = self.get_corpus_path()

        # If there is no path, create one.
        corpus_path.mkdir(parents=True, exist_ok=True)

        # Save the original text of books
        for current_work in self.__work_list:
            current_work.save_data_file_to(corpus_path)

    def to_dict(self):
        """Convert to python dict for general purpose.
        Returns:
            dict: A python dictionary containing the metadata of the books in the corpus.

        Example:
            >>> from pprint import pprint
            ...  corpus = Corpus("corpus", "WD/corpora")
            ... pprint(corpus.to_dict())
            # {0: {'author_aliases': {'Αριστοφάνης', 'Ἀριστοφάνης'},
            #     'author_birth_date': '1873',
            #     'author_death_date': '1924',
            #     'author_gutenberg_aliases': {'Αριστοφάνης', 'Ἀριστοφάνης'},
            #     'author_gutenberg_id': 'http://www.gutenberg.org/2009/agents/965',
            #     'book_gutenberg_id': 'http://www.gutenberg.org/ebooks/2571',
            #     'book_title': 'Peace'
            #     ...},
            # 1: {'author_aliases': set(),
            #     'author_birth_date': '-450',
            #     'author_death_date': '-388',
            #     'author_first_name': 'John',
            #     'author_gutenberg_aliases': set(),
            #     'author_gutenberg_id': 'http://www.gutenberg.org/2009/agents/979',
            #     'book_title': 'The Bicyclers and Three Other Farces'
            #     ...},
            # ...
            # }

        """
        corpus_dict = {}
        for index, current_work in enumerate(self.__work_list):
            work_dict = current_work.to_dict()
            file_path = self.get_corpus_path() / current_work.get_data_file_name()
            if file_path.exists():
                work_dict["text_file_path"] = file_path
            corpus_dict[index] = work_dict
        return corpus_dict

    def to_pandas_dataframe(self):
        """Convert the list of books into a pandas.DataFrame.

        Returns:
          pandas.DataFrame:

        Example:
            >>> corpus = Corpus("corpus", "WD/corpora")
            ... corpus.to_pandas_dataframe()
            #  author_aliases  ...                                     text_file_path
            # 0             {}  ...  /home/megloff1/Desktop/jane_austen/158-gutenbe...
            # 1             {}  ...  /home/megloff1/Desktop/jane_austen/25946-guten...
            # 2             {}  ...  /home/megloff1/Desktop/jane_austen/19839-guten...
            # 3             {}  ...  /home/megloff1/Desktop/jane_austen/22953-guten...
            # 4             {}  ...  /home/megloff1/Desktop/jane_austen/1212-gutenb...
            # 5             {}  ...  /home/megloff1/Desktop/jane_austen/22954-guten...
            # 6             {}  ...  /home/megloff1/Desktop/jane_austen/22962-guten...
            # 7             {}  ...  /home/megloff1/Desktop/jane_austen/121-gutenbe...
            # [8 rows x 15 columns]


        """
        import pandas as pd

        work_list = []
        for current_work in self.__work_list:
            work_dict = current_work.to_dict()
            file_name = current_work.get_data_file_name()
            file_path = self.get_corpus_path() / file_name
            if file_path.exists():
                work_dict["data_file_path"] = file_path
            work_list.append(work_dict)
        return pd.DataFrame(work_list)

    def __iter__(self):

        """
        Add capability to iterate over books in corpus.

        Returns:
            iterator: iter
                An iterator over the books in the corpus's booklist.
        """
        for current_work in self.__work_list:
            yield current_work

    def __len__(self):

        """
        List length.

        Returns:
            len (int):
                The number of books in the corpus.
        """
        return len(self.__work_list)

    def __str__(self):
        """
        Convert book_list in string format.

        Returns:
            corpus_str (str):
                A string of books in the list with information like the number of current_work in the list,
                author's name and the title the current_work.

        """
        # Add padding to the authors' name in order to have a clean string
        max_author_name_len = max([
            len(current_work.get_author().get_full_name()) for current_work in self.__work_list
        ]) + 4
        format_string = "{}\t{:" + str(max_author_name_len) + "}\t{}"
        return "\n".join([
            format_string.format(
                i, current_work.get_author().get_full_name(), current_work.get_title()
            ) for i, current_work in enumerate(sorted(self.__work_list))
        ])

    def __getitem__(self, index: int):
        """
        Return the current_work requested.

        Parameters:
            index (int): The index of the current_work in the corpus

        Returns:
            str : the current_work from the current_work list

        """
        return self.__work_list[index]
