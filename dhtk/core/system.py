# coding=utf-8
# coding=utf-8
"""Utility functions used by all modules."""
import importlib
import subprocess
import sys
import datetime
import typing
import pathlib
import logging
import warnings
import platform
import requests
import tqdm

# noinspection PyPackageRequirements
import __main__ as main
IS_INTERACTIVE = not hasattr(main, '__file__') or __name__ == "__main__"

logger = logging.getLogger(__name__)

warnings.formatwarning = lambda message, *args: f"{message}\n"


def get_platform():
    """Returns computes platform."""
    return f'"({platform.system()}; U; {platform.architecture()[0]}; en-us)"'


# noinspection PyUnusedFunction
def make_dirs(directories: typing.Union[str, typing.List[str]]) -> None:
    """Function to create new directories at DHTK's initiation.

    Args:
      directories (typing.Union[str, typing.List[str]]): the new directory path

    """
    # Convert values to list
    if not isinstance(directories, list):
        directories = [directories]

    # For each directory, confirm value is a pathlib.Path object and directory doesn't exist
    for directory in directories:
        directory = pathlib.Path(directory)

        if not directory.is_dir():
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except (IOError, PermissionError):
                sys.exit(f"Could not create {directory}, please check user rights.")


def url_exists(url: str):
    """Function to check if an url is available.

    Args:
      url (str): the path to check

    """

    # If the URL is a local file
    if url.startswith("file:"):
        return pathlib.Path(url.split("/", 1)[1]).exists()

    # If URL is a remote file
    try:
        response = requests.head(url)
    except requests.exceptions.ConnectionError:
        return False
    return response.ok


def download_files(
        urls: typing.Union[str, typing.List[str]],
        path:  typing.Union[str, pathlib.Path] = "./",
        file_names: typing.Optional[typing.Union[str, typing.List[str]]] = "") -> \
        typing.Union[str, typing.List[str]]:
    """Function to download files from the Web.

    Args:
      urls (typing.Union[str, typing.List[str]]): URLs of the files to be downloaded
      path (str, optional): Path to directory to store the downloaded files. (Default value = "./")
      file_names (typing.Union[str, typing.List[str], optional): Output name or names of the files to be downloaded.


    """

    # Convert inputs to list
    if isinstance(urls, str):
        urls = [urls]

    if isinstance(path, str):
        path = pathlib.Path(path)
    path.mkdir(exist_ok=True)

    # Request all files
    get_file_names = False
    if not file_names:
        file_names = []
        get_file_names = True
    elif isinstance(file_names, str):
        file_names = [file_names, ]
    elif isinstance(file_names, list):
        if len(file_names) != len(urls):
            raise IndexError("The list of filenames should correspond to the list of urls.")
    for index, url in enumerate(urls):

        if url_exists(url):  # Check if URL is valid
            if get_file_names:
                file_name = url.split('/')[-1]
                file_name = file_name.split('?')[0]
            else:
                file_name = file_names[index]

            file_paths: typing.List[pathlib.Path] = [path / file for file in file_names]
            if all(file.exists() for file in file_paths):
                if len(file_paths) == 1:
                    return file_paths[0].name
                return [file_path.name for file_path in file_paths]
            # Make request
            headers = {'User-Agent': get_platform()}
            with requests.get(url, stream=True, headers=headers) as request:
                request.raise_for_status()
                chunk = 8192
                total = int(request.headers['Content-Length'])

                # Read to file
                with open(path / file_name, 'wb') as out_file:
                    with tqdm.tqdm(total=total, desc=f"Downloading {file_name}") as progress_bar:
                        for part in request.iter_content(chunk_size=chunk):
                            out_file.write(part)
                            progress_bar.update(chunk)
                logger.info("DOWNLOAD: %s downloaded from  %s to %s", file_name, url, path)
        else:  # Warn if URL is not valid
            msg = f"URL not available: {url}"
            warnings.warn(msg)
            logger.warning("DOWNLOAD: %s", msg)

    if len(file_names) == 1:  # Return a string if there is only one file
        file_names = file_names[0]

    return file_names


# noinspection PyUnusedFunction
def get_date(url: str) -> datetime.datetime:
    """Function to get last modified date of a remote file

    Args:
      url (str): the url link

    Returns:
      datetime (datetime): the datatime object
    """

    headers = {'User-Agent': get_platform()}
    request = requests.head(url, stream=True, headers=headers)
    request = request.headers['last-modified']
    last_update = datetime.datetime.strptime(request, '%a, %d %b %Y %H:%M:%S %Z')

    return last_update


def pip_install(module_type, module):
    """
    Helper function to install missing modules

    Args:
        module_type (str): possible values "data_sources"  or "storage"
        module: "the dhtk module name"

    Returns:
        the imported module.

    """
    if 'dummy' in module:
        module_name = f"dhtk_{module_type.rstrip('s')}_{module}"
        module_import = f"dhtk.{module_type}.{module}"
        git_url = f"git+ssh://git@gitlab.com/dhtk/dhtk_{module_type}/examples/{module_name}"
    else:
        module_name = f"dhtk_{module_type}_{module}"
        module_import = f"dhtk.{module_type.rstrip('s')}.{module}"
        git_url = f"git+ssh://git@gitlab.com/dhtk/dhtk_{module_type}s/{module_name}"
    if not IS_INTERACTIVE:
        raise EnvironmentError(f"This method is for interactive usage only! Please install {module_name} manually:"
                               f"$ pip install {git_url}")
    answer = input(f"Do you want dhtk to install {module_name}? [y/N]")
    if not answer.lower().startswith("y"):
        raise EnvironmentError(f"Please install the module manually: $ pip install {git_url}")
    try:
        cmd = ['-m', 'pip', 'install', git_url]
        subprocess.check_call([sys.executable] + cmd)
    except subprocess.CalledProcessError:
        msg = f"Module {module_name} not available."
        warnings.warn(msg)
        logger.error("DATASET: %s", msg)
    return importlib.import_module(
        module_import
    )
