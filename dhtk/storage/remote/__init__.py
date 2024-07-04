# coding=utf-8
"""The remote storage module.

This module holds a dummy remote module for code simplicity in dhtk.core.
Users using the remote storage type should set up and handle the storage associated with the endpoint.
"""
import logging
import pathlib
import typing
from dhtk.storage.blueprint import AbstractStorage


logger = logging.getLogger(__name__)


# noinspection PyUnusedClass
class Storage(AbstractStorage):
    """The storage just handles config as the remote endpoint is set up and controlled by the user.
    """
    config = {}

    def __init__(self, working_directory: pathlib.Path) -> None:
        self.working_directory = working_directory

    def close(self):
        """

        """
        pass

    def start(self, config: typing.Dict[str, pathlib.Path]) -> None:
        """

        Args:
            config:
        """
        data_source = config["name"]
        storage_type = config["type"]
        self.config[data_source] = self.config.get(data_source, {})
        self.config[data_source][storage_type] = self.config[data_source].get(storage_type, {})
        self.config[data_source][storage_type].update(config)

    def get_endpoint(self, data_source_name: str, storage_type: str) -> str:
        """

        Args:
            data_source_name:
            storage_type:

        Returns:

        """
        return self.config[data_source_name][storage_type]["endpoint"]
