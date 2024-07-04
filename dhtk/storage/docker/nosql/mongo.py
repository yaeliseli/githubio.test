# coding=utf-8
from dhtk.storage.docker import AbstractStorageBackend


# noinspection PyUnusedClass
class Backend(AbstractStorageBackend):

    name = "mongo"
    docker_config = {
        "image": "docker.io/mongo",
        "endpoint": "mongodb://localhost:27017/dhtk",
        "config": {
           "ports": {27017: 27017},
        },
        "init.js": """
        db = db.getSiblingDB('dhtk');
        db.createCollection("dhtk");
        """,
        "init.sh": """
        #!/bin/bash"
        if [ -d /tmp/data ]; then
        for i in /tmp/data/*; do
            echo "importing ${i:10}"
            mongoimport -d dhtk -c dhtk --file $i
        done
        rm -r /tmp/data
        fi
        """,
        "dockerfile": """
            FROM docker.io/mongo

            ENV SETUP_SCRIPT=/docker-entrypoint-initdb.d/init-1.js
            ENV IMPORT_SCRIPT=/docker-entrypoint-initdb.d/init-2.sh
            RUN mkdir /tmp/data
            COPY nosql/*.json /tmp/data/
            COPY init.js /docker-entrypoint-initdb.d/init-1.js
            COPY init.sh /docker-entrypoint-initdb.d/init-2.sh
        """.replace("    ", "").replace("\t", ""),
    }

    def get_endpoint(self, port):
        """

        Args:
            port:

        Returns:

        """
        return self.docker_config["endpoint"].replace("27017", str(port))

    def get_docker_cmd(self, data_source_name, data_file_path):
        """

        Args:
            data_source_name:
            data_file_path:

        Returns:

        """
        return ["--bind_ip_all"]

    def get_dockerfile(self, data_source_name, data_file_path):
        """

        Args:
            data_source_name:
            data_file_path:

        Returns:

        """
        dockerfile = data_file_path.parents[0]/"Dockerfile"
        with dockerfile.open("w", encoding="latin1", newline='\n') as out_file:
            out_file.write(
                self.docker_config["dockerfile"]
            )
        js_init_file = data_file_path.parents[0]/"init.js"
        with js_init_file.open("w", encoding="latin1", newline='\n') as out_file:
            out_file.write(self.docker_config["init.js"])
        sh_init_file = data_file_path.parents[0]/"init.sh"
        with sh_init_file.open("w", encoding="latin1", newline='\n') as out_file:
            out_file.write(self.docker_config["init.sh"])
        return str(dockerfile), f"dhtk/mongo_{data_source_name}"
