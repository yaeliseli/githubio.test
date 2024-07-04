# coding=utf-8
"""
Contains GutenbergTexts Class.


Notes
-----
This class is being reworked.
The cleaning of the texts was adapted from: https://github.com/okfn/gutenizer
"""
import pathlib
import re
import shutil
import warnings
import zipfile
import logging

from pathlib import Path
from tempfile import mkdtemp

import chardet
import requests

from dhtk.core.system import url_exists, download_files

logger = logging.getLogger(__name__)


warnings.formatwarning = lambda message, *args: f"{message}\n"


def extract_book(path, destination=None):
    """

    Args:
      path(str): Path of the archive of a book. A Zip file containing a single txt file.
      destination(str, optional): Path where the texfile should be extracted. (Default value = None)

    Returns:

    """
    title = path.rsplit("/", 1)[1].replace(".zip", "")
    with zipfile.ZipFile(path, 'r') as archive:
        raw_text = ""
        for txt_file in archive.namelist():
            print(title)
            if txt_file.endswith(".txt"):
                raw_text = archive.read(txt_file)
                break

    detect = chardet.detect(raw_text)

    raw_text = raw_text.decode(detect["encoding"])
    if destination:
        try:
            with open(destination, "w")as out_file:
                out_file.write(destination)
        except IOError as error:
            raise IOError(f"Path could not be written: {destination}") from error

    return raw_text


class GutenbergTexts:
    """
    Clean up Gutenberg texts by removing all the header and footer.

    Args:

    Returns:

    Notes
    -----
    Part of this class have to be reworked.

    Usage : init and then run _extract_text.
    _notes_end = ""
    _header_end = ""
    _footer_start = ""
    _original_text = ""
    _clean_text = ""
    _url = ""

"""
    def __init__(self, book, repository_uri='http://aleph.gutenberg.org'):
        """
        Init function of the GutenbergTexts.

        Check repository_uri and create a temporary directory for file operations.
        repository_uri: can be local file:/path/to/dir
        refer to:
        https://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages
        to download the files.

        Parameters
        ------------------
        repository_uri : str
            Can be a file uri file://home/user/Documents/gutenberg_dump or
            a http uri: http://aleph.gutenberg.org
        """
        self._original_text = None
        if not repository_uri:
            raise ValueError("Please set the URI of a 'local' gutenberg text repository.")

        if "http://www.gutenberg.org/files" in repository_uri:
            raise ValueError(
                """
                Please create a local repository. More information on:
                https://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages
                """
            )

        self._temporary_dir = Path(mkdtemp(prefix="dhtk-"))
        self._repository_uri = repository_uri
        self.book = book

    def get_original_text(self):
        """Returns original text of a given book."""

        found_url = False
        url = ""
        if self._original_text:
            return self._original_text

        base_url = self._repository_uri + "/" + self.book.get_text_file_dir_path()

        valid_extensions = ("-0.txt", "-8.txt", ".txt")
        if self._repository_uri.startswith("file://"):
            valid_extensions = ("-0.txt", "-8.txt", ".txt", "-0.zip", "-8.zip", ".zip")
        for extension in valid_extensions:
            url = base_url + extension
            try:
                found_url = url_exists(url)
            except requests.exceptions.ConnectionError:  # aleph is not reliable, just use gutenberg directly for now
                url = re.sub(self._repository_uri, "http://www.gutenberg.org/files", url)
                gutenberg_id = self.book.get_book_id_number()
                url = re.sub(self.book.get_text_file_dir_path(), f"{gutenberg_id}/{gutenberg_id}", url)

                found_url = url_exists(url)

            if found_url:
                break

        # TODO: once search does not find audio editions anymore uncomment this:
        # if not found_url:
        #     raise Warning(
        #        "Could not find the text file for {} {}.".format(
        #           book.get_author(),
        #           book.get_title()
        #       )
        #    )
        # TODO: once search does not find audio anymore editions remove this:
        if not found_url:
            return None

        try:
            raw_file_path = download_files(
                url,
                self._temporary_dir / self.book.get_text_file_name(),
                self.book.get_title()
            )
            if raw_file_path.endswith(".zip"):
                self._original_text = extract_book(raw_file_path)
                path = pathlib.Path(raw_file_path)
                path.unlink()

            else:
                with open(raw_file_path, "r", encoding="utf8", errors='ignore') as book_text_file:
                    self._original_text = book_text_file.read()
                path = pathlib.Path(raw_file_path)
                path.unlink()

        except Exception as ex:
            raise ex

        return self._original_text

    def save_original_text_file_to(self, destination):
        """Save the original text to a text-file in or at destination.

        Args:
          destination(str): Path of the destination where the text will be saved.

        Returns:

        """
        destination = pathlib.Path(destination)
        filename = self.book.get_text_file_name()
        filename = destination / filename
        if filename.is_file() and filename.stat().st_size == 0:
            return filename

        self.get_original_text()

        if not destination.is_dir():
            destination.mkdir(parents=True, exist_ok=True)

        try:
            with open(filename, "w", encoding='utf8') as file_writer:
                file_writer.write(self._original_text)
        except IOError:
            # LOGGER.warning("File %s could not be created.", filename)
            print("File %s could not be created.", filename)
        return filename

    # def save_clean_text_file_to(self, destination):
    #     """Save the clean text to a text-file in or at destination.
    #
    #     Args:
    #       destination(str): Path of the destination where the text will be saved.
    #
    #     Returns:
    #
    #     """
    #     self.get_original_text()
    #
    #     destination = Path(destination)
    #
    #     if not destination.is_dir():
    #         destination.mkdir(parents=True, exist_ok=True)
    #
    #     filename = self.book.get_text_file_name()
    #
    #     filename = destination / filename
    #     if not filename.is_file() or filename.stat().st_size == 0:
    #         with open(filename, "w") as file_writer:
    #             file_writer.write(self._clean_text)
    #
    #     return filename

    def __del__(self):
        try:
            if self._temporary_dir.is_dir():
                shutil.rmtree(self._temporary_dir)
        except NameError:
            pass

    def close(self):
        """Remove temporary directory if instance is closed."""
        try:
            if self._temporary_dir.is_dir():
                shutil.rmtree(self._temporary_dir)
        except NameError:
            pass
