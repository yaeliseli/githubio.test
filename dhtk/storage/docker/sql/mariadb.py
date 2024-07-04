# coding=utf-8

from dhtk.storage.docker import AbstractStorageBackend


# noinspection PyUnusedClass
class Backend(AbstractStorageBackend):
    """
    Backend configuration for mariadb
    """
    name = "mariadb"
    docker_config = {
        "image": "mariadb",
        "endpoint": "mariadb://user:dhtk@127.0.0.1:3306/dhtk",
        "config": {
            "ports": {3306: 3306},
            "environment": [
                "MARIADB_USER=user",
                "MARIADB_PASSWORD=dhtk",
                "MARIADB_ROOT_PASSWORD=dhtk",
                "MARIADB_DATABASE=dhtk",
                "MARIADB_ROOT_HOST=127.0.0.1",
            ],
            "volumes": {
                "data_load_directory": {'bind': '/docker-entrypoint-initdb.d', 'mode': 'ro'}
            },
           },
        }

    def get_endpoint(self, port):
        """

        Args:
            port:

        Returns:

        """
        return self.docker_config["endpoint"].replace("3306", str(port))

    def get_docker_cmd(self, data_source_name, data_file_path):
        """

        Args:
            data_source_name:
            data_file_path:

        Returns:

        """
        return ["--port=3306", "--bind_address=0.0.0.0", "--skip-networking=0", "--skip_name_resolve=0"]
