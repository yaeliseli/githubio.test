# coding=utf-8
"""DHTK core modules."""

# import dependencies
import copy
import pathlib
import typing
import warnings
import importlib
import logging
from pkgutil import iter_modules
from pprint import pprint

from dhtk import data_sources as dhtk_data_sources
from dhtk import storage as dhtk_storage
from dhtk.core.system import pip_install, IS_INTERACTIVE
from dhtk.corpus import Corpus

warnings.formatwarning = lambda message, *args: f"{message}\n"

__all__ = ("start", "IS_INTERACTIVE", "AVAILABLE_STORAGES", "AVAILABLE_DATA_SOURCES")
logger = logging.getLogger(__name__)

# store alla available data sources already installed in python packages
AVAILABLE_DATA_SOURCES = [
    module.name for module in iter_modules(path=dhtk_data_sources.__path__)
    if module.name not in ("blueprint", "templates")
]

# store alla available storage type (SQL,NoSQL, etc) already installed in python packages
AVAILABLE_STORAGES = [
    module.name for module in iter_modules(path=dhtk_storage.__path__)
    if module.name != "blueprint"
] + ["embedded", ]


class DhTk:
    """
    DhTk class. This class is the main interface of dhtk.
    Its purpose is multiple:

        1. check available storage and data_source modules and load them correctly.
        2. link data_sources to the needed storages.
        3. handle users arguments and configurations.
        4. setup logging.
        5. provide methods to federate data handling over all data_sources.
    """

    def __init__(
            self,
            working_directory: typing.Union[str, pathlib.Path],
            corpus_name: str,
            config
    ):
        """
        Instantiate a DHTK Settings data object and prints current settings.

        Args:
            working_directory:  the path to DHTK's working directory,
                                if empty it uses the current working directory.
            corpus_name:
            config:
                a dictionary of dictionary

        See Also:

            see `dhtk.start()` function documentation.
        """

        self.storage = {}
        self.data_sources = {}
        self.config = config
        self.endpoints = {}

        if isinstance(working_directory, str):
            working_directory = pathlib.Path(working_directory)
        self.working_directory = working_directory
        self.working_directory.mkdir(parents=True, exist_ok=True)

        # Check config format
        data_sources = {}

        config, data_sources = self.__set_storage(config, data_sources)

        for data_source_name, data_source_module in data_sources.items():
            endpoints = []
            for storage_type in config[data_source_name].keys():
                if storage_type == "embedded":
                    continue
                endpoints.append(self.endpoints[data_source_name][storage_type])
            # noinspection PyUnresolvedReferences
            self.data_sources[data_source_name] = data_source_module.Module(
                working_directory=f"{self.working_directory.name}/{data_source_name}",
                endpoints=endpoints
            )

        corpora_path = working_directory / "corpora"
        corpus_path = corpora_path / corpus_name
        corpus_path.mkdir(parents=True, exist_ok=True)
        self.corpus = Corpus(corpus_name, corpora_path.name)

        config["corpus_name"] = corpus_name
        config["corpora_path"] = corpora_path.name

        self.config = config

        if IS_INTERACTIVE:
            print(f"Current DHTK settings:\n{self.config}")

    def __set_storage(self, config: dict, data_sources: dict) -> typing.Tuple[dict, dict]:
        """
        Prepares storage config and checks config.
        """
        # split config in 2 variable (i.e. data_source='gutenberg' and data_source_config={'storage': 'docker'})
        for data_source, data_source_config in copy.deepcopy(config).items():
            self.storage[data_source] = {}
            self.endpoints[data_source] = {}

            # check if data_source is installed (i.e. AVAILABLE_DATA_SOURCES=['dummysql', 'dummytei', 'gutenberg'])
            if data_source not in AVAILABLE_DATA_SOURCES:
                raise ModuleNotFoundError(
                    f"Data source is not available: {data_source}\n"
                    f"Quick fix:\n$ pip install dhtk_data_source_{data_source}"
                )

            # if data_source is installed then load the data source from the python packages
            # data_source_module = import "dhtk.data_sources.gutenberg"
            data_source_module = importlib.import_module(
                "dhtk.data_sources." + data_source
            )

            # set the value of data_sources with the module key
            # with the data_source module  from the package library
            # (i.e. data_sources['gutenberg']=<module 'dhtk.data_sources.gutenberg'>)
            data_sources[data_source] = data_source_module

            # get the value of the variable 'storage_type' from the specified module
            # (ie. from <class 'dhtk.data_sources.gutenberg.Module'> returns 'needed_storages' = 'triplestore')
            # noinspection PyUnresolvedReferences
            needed_storages = getattr(data_source_module.Module, "storage_type")

            # if it is a string, transform 'need_storages' into a list
            if isinstance(needed_storages, str):
                needed_storages = [needed_storages, ]

            # if needed_storages is not set in the module, the set it to "embedded" by default
            if len(needed_storages) == 0:
                self.storage[data_source]["embedded"] = {}

            # elif needed_storages list is composed by just one element
            elif len(needed_storages) == 1:
                # get the only element and store it into needed_storage
                needed_storage = needed_storages[0]
                # if needed_storage == "embedded" save into self.storage
                if needed_storage == "embedded":
                    self.storage[data_source]["embedded"] = {}
                # if needed_storage (i.e. triplestore) does not appear in
                # 'config' like this :"'gutenberg': {'triplestore': {'storage': 'docker'}}}",
                # then process to be like this.
                # (i.e  config="'gutenberg': {'storage': 'docker'}} -->
                # config='gutenberg': {'triplestore': {'storage': 'docker'}}})
                if needed_storage not in config[data_source].keys():
                    data_source_name = data_source
                    tmp = config.pop(data_source)
                    config[data_source_name] = {}
                    config[data_source_name][needed_storage] = tmp
            else:
                for needed_storage in needed_storages:
                    if needed_storage not in config[data_source].keys():
                        raise RuntimeError(
                            f"Missing storage configuration for data source {data_source}: "
                            f"configure storage of type {needed_storage}."
                        )

            # set data_source and needed_storages in self.storage
            # (i.e. needed_storages={'gutenberg': {'triplestore': {}}})
            for needed_storage in needed_storages:
                self.storage[data_source][needed_storage] = {}

                # create the dirs and sub dirs for the configuration using
                # data_source and needed_storage and returns a dict storage_module_config
                # (i.e. data_source='gutenberg', needed_storage='triplestore' --->
                # storage_module_config={'data_dir': PosixPath('WD/gutenberg/data/triplestore'),
                # 'storage_dir': PosixPath('WD/gutenberg/storage/triplestore')}
                storage_module_config = self.__make_filestorage(data_source, needed_storage)
                if needed_storage == "embedded":
                    continue

                # Store the function method for getting the data file as defined into the function "get_data_file"
                # from the module import (ie <module 'dhtk.data_sources.gutenberg'
                # from '/site-packages/dhtk/data_sources/gutenberg/__init__.py'>)
                storage_module_config["get_file_function"] = getattr(
                    data_source_module.Module, "get_data_file"
                )
                # Store the parameters to pass the function
                # (ie PosixPath('WD/gutenberg/data/triplestore', 'triplestore')
                storage_module_config["get_file_args"] = (
                    storage_module_config["data_dir"], needed_storage
                )
                # Store the name of the data source (ie. 'gutenberg')
                storage_module_config["name"] = data_source

                # Store the name of the storage (ie 'triplestore')
                storage_module_config["type"] = needed_storage

                # If setting to endpoint
                if "endpoint" in data_source_config:
                    storage_module_config["endpoint"] = data_source_config["endpoint"]

                # if 'storage' set
                if "storage" in config[data_source][needed_storage]:
                    # get storage_module_name (ie 'docker')
                    storage_module_name = config[data_source][needed_storage]["storage"]
                    # save it into storage_module_config
                    storage_module_config["module_name"] = storage_module_name
                    if storage_module_name == "embedded":
                        continue
                    # try to import the module of the corresponding storage method (i.e. 'docker')
                    try:
                        storage_module = importlib.import_module(
                            "dhtk.storage." + storage_module_name
                        )
                    except BaseException as error:
                        raise ModuleNotFoundError(
                            "Not all storage modules you selected are available."
                        ) from error

                    # set the storage module in the storage variable
                    # noinspection PyUnresolvedReferences
                    self.storage[data_source][needed_storage]["module"] = storage_module.Storage(
                        self.working_directory
                    )

                    # call docker storage `start` function [dhtk/storage/docker/__init__.py]
                    self.storage[data_source][needed_storage]["module"].start(storage_module_config)

                    self.endpoints[data_source] = self.endpoints.get(data_source, {})

                    # get and set the endpoint variable in the storage variable
                    self.endpoints[data_source][needed_storage] = \
                        self.storage[data_source][needed_storage]["module"].get_endpoint(
                            data_source, needed_storage
                        )

                self.storage[data_source][needed_storage]["config"] = storage_module_config

        return config, data_sources

    def __make_filestorage(self, data_source, needed_storage):
        """
        Prepare the directories for storage in the working directory
        Args:
            data_source (str): the name of data source (i.e 'gutenberg)
            needed_storage (str):  the name of storage (i.e 'sql')

        Returns:
            dict: a dictionary with the data dir and the storage dir

        """

        if not self.working_directory.exists():
            raise FileNotFoundError(
                f"Make sure your working directory: {self.working_directory} exists!")

        data_source_dir = self.working_directory / data_source
        if not data_source_dir.exists():
            data_source_dir.mkdir(parents=True, exist_ok=True)

        data_dir = data_source_dir / "data" / needed_storage
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)

        storage_dir = data_source_dir / "storage" / needed_storage
        if not storage_dir.exists():
            storage_dir.mkdir(parents=True, exist_ok=True)
        return {"data_dir": data_dir, "storage_dir": storage_dir}

    def get_available_corpora(self):
        """Get the names of available corpora."""
        corpora_path = self.working_directory / "corpora"
        return [corpus.stem for corpus in sorted(corpora_path.iterdir()) if corpus.is_dir()]

    def get(self, *args: str, **kwargs: typing.Union[str, bool]):
        """
        This function uses the get() in the loaded data sources to get all results.
        Args:
            *args (list): the args in the get() function defined in the data source
            **kwargs (dict): the kwargs in the get() function defined in the data source

        Returns:
            list: results of the query

        """
        add = kwargs.get("add", False)
        results = {}
        if len(args) == 1:
            if args[0] == "corpus":
                results = self.corpus.get_info()
            elif args[0] == "corpora":
                results = self.get_available_corpora()

        if not results:
            for name, data_source in self.data_sources.items():
                logger.info("Getting from %s", name)
                results[name] = data_source.get(*args, **kwargs)
            if results:
                if len(self.data_sources) == 1:
                    results = results[next(iter(self.data_sources))]
                if add:
                    self.corpus.add_works(results)
                else:
                    if add:
                        for data_source, values in results.items():
                            self.corpus.add_works(values)
        if IS_INTERACTIVE:
            pprint(results)

        return results

    def search(self, *args: str, **kwargs: typing.Union[str, bool]):
        """
        This function uses the get() in the loaded data sources to get all results.
        Args:
            *args: the args in the get() function defined in the data source
            **kwargs: the kwargs in the get() function defined in the data source

        Returns:
            list: results of the query

        """
        results = {}
        if len(args) == 1:
            if args[0] == "corpus":
                results = self.corpus.get_info()
            elif args[0] == "corpora":
                results = self.get_available_corpora()

        if not results:
            for name, data_source in self.data_sources.items():
                logger.info("Searching in %s", name)
                results[name] = data_source.search(*args, **kwargs)
            if len(self.data_sources) == 1:
                results = results[next(iter(self.data_sources))]
        if IS_INTERACTIVE:
            pprint(results)
        return results

    def __del__(self) -> None:
        for storage in self.storage.values():
            for storage_backend in storage.values():
                storage_backend["module"].close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        for storage in self.storage.values():
            for storage_backend in storage.values():
                storage_backend["module"].close()

    def __delattr__(self, item):
        if item == "storage":
            for storage in self.storage.values():
                for storage_backend in storage.values():
                    storage_backend["module"].close()


def start(*args: str, **kwargs) -> DhTk:
    """
    Check the configuration setting and instantiate DhTk.
    Args:
        *args: The working_directory. The path  to the working directory, by default the current location.
        **kwargs: for the other parameters there can be different usages:

            config: dict of dict containg all arguments of type:

                {data_source}={"endpoint": {"endpoint or connection string", [update=bool]}}, or

                {data_source}={"storage": "a dhtk storage module name"}.

            where storage is  a dhtk storage module name and `data_source` is the name of a dhtk data source module, or
            `data_sources is a list of dhtk data source module names.

    Returns:
        DhTk: A DHTK object.

    Examples:
        This is a working example of how to run multiple datasources.

        >>> import dhtk
        >>> d  = dhtk.start("WD", config={"gutenberg": {"storage":  "docker"}, "auchinleck": {"storage": "docker" }})

        These are other working examples.

        >>> import dhtk
        >>> d = dhtk.start("WD", config={"gutenberg":{'triplestore' : {"storage":  "docker"}}})

        >>> import dhtk
        >>> d = dhtk.start("WD", data_source="gutenberg", storage="docker")

        >>> import dhtk
        >>> d = dhtk.start("WD", "corpus_name", data_sources=["gutenberg", "auchinleck"], storage="docker")

        >>> import dhtk
        >>> a = dhtk.start("WD", config={"auchinleck": {"storage": "docker" }})  # for test purposes
        >>> d = dhtk.start("WD", corpus="corpus_name", gutenberg={"storage": "docker"},
        ...                auchinleck={"endpoint": "http://localhost:3030/ds/sparql" } )


    """

    # first argument should be only the working directory path
    if len(args) > 2:
        raise TypeError(f"start() takes 1 or 2 positional arguments but {len(args)} was given")

    # set the default working_directory path to the current path if not found in args or in kwargs
    working_directory = "."
    corpus_name = None
    if args:
        working_directory = args[0]
        if len(args) == 2:
            corpus_name = args[1]
    elif "working_directory" in kwargs:
        working_directory = kwargs.pop("working_directory")

    if not corpus_name:
        if "corpus" in kwargs:
            corpus_name = kwargs.pop("corpus")
        else:
            corpus_name = "corpus"

    # config is equal to the parameters given in the command line i.e. config={'gutenberg': {'storage': 'docker'}}
    config = kwargs.get("config", {})

    # set the default 'data_sources' dict key to the current path if not found in args or in kwargs
    data_sources = kwargs.get("data_sources", [])

    # if 'data_source' in kwargs, then get it otherwise
    if "data_source" in kwargs:
        data_sources += [kwargs.get("data_source", None)]

    # if there is no "data_source(s)", set all config.keys() to "data_source" dict key as default.
    # so  i.e. config={'gutenberg': {'storage': 'docker'}} set 'data_source'=['gutenberg']
    if (not data_sources) and config:
        data_sources = [str(data_source) for data_source in config.keys()]

    # set storage,endpoint and update to default values
    storage = kwargs.get("storage", None)
    endpoint = kwargs.get("endpoint", None)
    update = kwargs.get("update", False)

    # if config is empty and storage or endpoint is not empty and data_sources is not empty then
    if (not config) and (isinstance(endpoint, str) or isinstance(storage, str)) and data_sources:
        for data_source in data_sources:
            try:
                data_source_module = importlib.import_module(
                    "dhtk.data_sources." + data_source
                )
            except ImportError as error:

                if IS_INTERACTIVE:
                    data_source_module = pip_install("data_sources", data_source)
                else:
                    raise ModuleNotFoundError(
                        f"The data sources you selected is not available : {data_source}"
                    ) from error

            # get the storage type from the datasource installed in the python packages
            # noinspection PyUnresolvedReferences
            storage_types = getattr(data_source_module.Module, "storage_type")

            if isinstance(storage_types, str):
                storage_types = [storage_types, ]

            # add storage and endpoint to the configuration, needed for the storage modules
            config[data_source] = {}
            for storage_type in storage_types:
                config[data_source][storage_type] = {}
                config[data_source][storage_type]["update"] = update
                if storage in AVAILABLE_STORAGES:
                    config[data_source][storage_type]["storage"] = storage
                else:
                    if IS_INTERACTIVE:
                        pip_install("storage", storage)
                    else:
                        raise ModuleNotFoundError(
                            f"The storage you selected is not available : {storage}"
                        )
                if endpoint:
                    config[data_source][storage_type]["endpoint"] = endpoint
                    config[data_source][storage_type]["storage"] = "remote"

    # if config is empty and any of the remaining kwargs values is dict of dict, then set it as config
    elif (not config) and all(isinstance(arg, dict) for arg in kwargs.values()):
        config = kwargs

    # if config is the only available resource then cannot be empty
    if not config:
        raise RuntimeError("No valid arguments!")

    # if endpoint is configured add storage as remote
    for key, value in config.items():
        if "endpoint" in value:
            value["storage"] = "remote"
            config[key] = value

    return DhTk(
        working_directory=pathlib.Path(working_directory),
        corpus_name=corpus_name,
        config=config
    )
