# coding=utf-8
from dhtk.storage.docker import AbstractStorageBackend


# noinspection PyUnusedClass
class Backend(AbstractStorageBackend):

    name = "mongo"
    docker_config = {
        "image": "secoresearch/fuseki",
        "endpoint": "http://admin:dhtk@localhost:3030/ds/sparql",
        "config": {
            "ports": {3030: 3030},
            "environment": [
                "ADMIN_PASSWORD=dhtk",
                "ENABLE_DATA_WRITE=true",
                "ENABLE_UPDATE=true",
                "ENABLE_UPLOAD=true",
                "QUERY_TIMEOUT=60000"
            ],

        },
        "init.sh": """
            #!/bin/bash
            if [ -d /tmp/data ]; then
                for i in /tmp/data/*; do
                    $TDBLOADER --graph="http://dhtk.unil.ch/${i:10:-4}" $i
            done
            $TEXTINDEXER
            $TDBSTATS --graph urn:x-arq:UnionGraph > /tmp/stats.opt
            mv /tmp/stats.opt /fuseki-base/databases/tdb
            rm -r /tmp/data
            fi
        """,
        "dockerfile": """
            FROM secoresearch/fuseki
            
            RUN mkdir /tmp/data && chown 9008 /tmp/data
            COPY --chown=9008 triplestore/* /tmp/data/
            COPY --chown=9008 init.sh /tmp/init.sh
            RUN chmod +x /tmp/init.sh
            RUN /tmp/init.sh            

        """.replace("    ", "").replace("\t", ""),
        "entrypoint_file": None,
    }

    def get_endpoint(self, port):
        """

        Args:
            port:

        Returns:

        """
        return f"http://localhost:{port}/ds/sparql"

    @staticmethod
    def get_endpoints(port):
        """

        Args:
            port:

        Returns:

        """
        return {
            "sparql": f"http://admin:dhtk@localhost:{port}/ds/sparql",
            "data": f"http://admin:dhtk@localhost:{port}/ds/data",
            "update": f"http://admin:dhtk@localhost:{port}/ds/update",
            "upload": f"http://admin:dhtk@localhost:{port}/ds/upload",
        }

    def get_dockerfile(self, data_source_name, data_file_path):
        """

        Args:
            data_source_name:
            data_file_path:

        Returns:

        """
        dockerfile = data_file_path.parents[0]/"Dockerfile"
        with dockerfile.open("w", encoding="utf-8", newline='\n') as out_file:
            out_file.write(
                self.docker_config["dockerfile"]
            )
        init_file = data_file_path.parents[0]/"init.sh"
        with init_file.open("w", encoding="utf-8", newline='\n') as out_file:
            out_file.write(
                self.docker_config["init.sh"]
            )
        return str(dockerfile), f"dhtk/fuseki_{data_source_name}"
