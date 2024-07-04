# coding=utf-8
from dhtk.storage.docker import AbstractStorageBackend


# noinspection PyUnusedClass
class Backend(AbstractStorageBackend):

    name = "basex"
    docker_config = {
        "endpoint": "basex://admin:admin@127.0.0.1:1984/",
        "image": "basex/basexhttp",
        "config": {
            "ports": {1984: 1984, 8984: 8984},
        },
        "dockerfile": """
            FROM basex/basexhttp
            
            USER root
            RUN mkdir /data/ && chown 1984 /data
            COPY --chown=1984 tei/* /data/
            ENV LOAD_DATA=/tmp/loaddata.cmd
            RUN echo 'CREATE DATABASE dhtk /data' > $LOAD_DATA \
            && echo 'FLUSH' >> $LOAD_DATA \
            && echo 'CLOSE' >> $LOAD_DATA \
            && echo '#!/bin/bash' > /tmp/load-data.sh \
            && echo '[ ! -e /tmp/flag ] && basex -c"/tmp/loaddata.cmd" && touch /tmp/flag' >> /tmp/load-data.sh \
            && echo '/usr/local/bin/basexhttp' >> /tmp/load-data.sh \
            && chmod +x /tmp/load-data.sh && chown 1984 /tmp/load-data.sh
            USER basex
            CMD ["/tmp/load-data.sh"]

        """.replace("    ", "").replace("\t", ""),
    }

    def get_endpoint(self, port):
        """

        Args:
            port:

        Returns:

        """
        return self.docker_config["endpoint"].replace("1984", str(port))

    def get_dockerfile(self, data_source_name, data_file_path):
        """

        Args:
            data_source_name:
            data_file_path:

        Returns:

        """
        dockerfile = data_file_path.parents[0] / "Dockerfile"
        with dockerfile.open("w", encoding="latin1", newline='\n') as out_file:
            out_file.write(
                self.docker_config["dockerfile"]
            )
        return str(dockerfile), f"dhtk/basex_{data_source_name}"
