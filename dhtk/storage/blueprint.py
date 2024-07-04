# coding=utf-8
"""Abstract class to be used as template for new extension modules __init__ script"""

# Import dependencies
import abc
import warnings
import socket

warnings.formatwarning = lambda message, *args: f"{message}\n"


class AbstractStorage(abc.ABC):

    @abc.abstractmethod
    def start(self, config):
        """

        Args:
            config:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        """

        """
        raise NotImplementedError

    def __del__(self):
        self.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __delete__(self, instance):
        instance.close()

    @staticmethod
    def is_port_in_use(port: int) -> bool:
        """
        Check if port is in use.

        Args:
            port: int
                  Port you with to check

        Returns: bool
                True if port is in use, else False.

        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            return sock.connect_ex(('localhost', port)) == 0
