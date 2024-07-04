# coding=utf-8
"""
This Dhtk Storage module control Docker.
"""
import abc
import time
import atexit
import logging
import importlib
from copy import deepcopy
from pkgutil import iter_modules
from docker import from_env
from docker.errors import DockerException, APIError, NotFound
from requests.exceptions import HTTPError
from dhtk.storage.blueprint import AbstractStorage

# noinspection PyPackageRequirements
import __main__ as main
IS_INTERACTIVE = __name__ == "__main__" or (not hasattr(main, '__file__'))

logger = logging.getLogger(__name__)

AVAILABLE_BACKENDS = [
                         module.name for module in iter_modules(path=__path__)
                     ]


class AbstractStorageBackend(abc.ABC):

    # noinspection PyPropertyDefinition
    @property
    @classmethod
    @abc.abstractmethod
    def docker_config(cls):
        """

        """
        raise NotImplementedError

    def get_docker_cmd(self, data_source_name, data_file_path):
        """

        Args:
            data_source_name:
            data_file_path:

        Returns:

        """
        return None

    def get_dockerfile(self, data_source_name, data_file_path):
        """

        Args:
            data_source_name:
            data_file_path:

        Returns:

        """
        return None, self.get_image()

    def get_image(self):
        """

        Returns:

        """
        return self.docker_config["image"]

    def get_config(self):
        """

        Returns:

        """
        return self.docker_config["config"]

    def get_endpoint_port(self):
        """

        Returns:

        """
        result = []
        ports = self.docker_config["config"]["ports"].keys()
        for port in ports:
            if isinstance(port, str):
                if "/" in port:
                    result.append(int(port.split("/")[0]))
                else:
                    result.append(int(port))
            elif isinstance(port, int):
                result.append(port)
        return result

    @abc.abstractmethod
    def get_endpoint(self, port):
        """

        Args:
            port:
        """
        raise NotImplementedError


class Storage(AbstractStorage):
    """
    Class for configuring Storage settings
    """

    instances = set()

    def __init__(self, working_directory, preferred_backends=None):
        """
        Initialize the Storage class

        Args:
            working_directory (str): the working directory path
            preferred_backends (str, optional):
                The preferred backend chosen for each storage_type

        """
        self.__class__.instances.add(self)
        self.endpoints = {}
        self.containers = set()
        self.working_directory = working_directory
        self.storages = {}
        try:
            self.docker_client = from_env()
        except (
                FileNotFoundError,
                ConnectionError,
                DockerException
        ) as exception:
            raise DockerException(
                "Could not connect to Docker! Make sure docker is running on your system!"
            ) from exception
        self.available_storages = {}
        self.available_backends = {}
        for storage in AVAILABLE_BACKENDS:
            module_path = f"{__path__[0]}/{storage}"
            aviliable_backends = [module.name for module in iter_modules(path=[module_path])]
            if len(aviliable_backends) > 1:
                if preferred_backends:
                    for backend in preferred_backends:
                        if backend in aviliable_backends:
                            self.available_backends[storage] = backend
                else:
                    module = importlib.import_module("dhtk.storage.docker" + storage)
                    self.available_backends[storage] = getattr(module, "DEFAULT")
            else:
                self.available_backends[storage] = aviliable_backends[0]

    @classmethod
    def get_instances(cls):
        """Return instances"""
        return cls.instances

    def start(self, config):
        """
        Starts the docker container

        Args:
            config (dict): The config settings for the docker (i.e.
            config = {'data_dir': PosixPath('WD/gutenberg/data/triplestore'),
            'storage_dir': PosixPath('WD/gutenberg/storage/triplestore'),
            'get_file_function': <bound method Module.get_data_file of <class 'dhtk.data_sources.gutenberg.Module'>>,
            'get_file_args': (PosixPath('WD/gutenberg/data/triplestore'), 'triplestore'),
            'name': 'gutenberg', 'type': 'triplestore', 'module_name': 'docker'}
            ).

        """

        file_path = ""
        image = ""
        data_source_name = config['name']
        storage_type = config["type"]
        self.storages[data_source_name] = {storage_type: {}}
        container_name = f"dhtk_{storage_type}_{data_source_name}"

        # get backend_module_name from the list 'mongo','mariadb','basex','fuseki'
        backend_module_name = self.available_backends[storage_type]

        # import the specific module
        backend_module = importlib.import_module(
            f"dhtk.storage.docker.{storage_type}.{backend_module_name}"
        )
        # call the class backend and store it
        # noinspection PyUnresolvedReferences
        self.storages[data_source_name]["backend"] = backend_module.Backend()

        port = int()
        container = None

        # try to run the docker container
        try:
            container = self.docker_client.containers.get(container_name)
            self.storages[data_source_name][storage_type]["container"] = container
            image = container.attrs['Config']['Image']
        # if not found
        except NotFound:

            # call the function to get the config settings
            docker_config = self.storages[data_source_name]["backend"].get_config()

            try:
                data_directory = str(config["storage_dir"].resolve())
                docker_config["volumes"][data_directory] = docker_config[
                    "volumes"
                ].pop("data_directory")
            except KeyError:
                pass
            try:
                file_dir = str(config["data_dir"].resolve())
                docker_config["volumes"][file_dir] = docker_config[
                    "volumes"
                ].pop("data_load_directory")
            except KeyError:
                pass
            # call the `get_file_function` stored in the dict and pass the config["get_file_args"] as *args
            config["get_file_function"](*config["get_file_args"])
            data_file_path = config['data_dir']
            # other configurations
            docker_config["detach"] = True
            docker_config["name"] = container_name
            ports = deepcopy(docker_config["ports"])
            for container_port, port in ports.items():
                while self.is_port_in_use(port):
                    port += 1
                docker_config["ports"][container_port] = port

            # get image and cmd from the object store in the dict
            # (i.e. 'backend': <dhtk.storage.docker.triplestore.fuseki.Backend object at 0x11aec3eb0>}}
            image = self.storages[data_source_name]["backend"].get_image()
            cmd = self.storages[data_source_name]["backend"].get_docker_cmd(
                data_source_name, data_file_path)

            orig_image = image
            dockerfile, image = self.storages[data_source_name]["backend"].get_dockerfile(
                data_source_name, data_file_path)

            rm_image = False
            if orig_image != image and image not in str(self.docker_client.images.list()):
                rm_image = True

            if dockerfile:
                logger.info(
                    "Building %s docker image and loading the data! This can take a while.",
                    image
                )
                response = []
                if IS_INTERACTIVE:
                    print("Building %s : ",  image, end="")
                for line in self.docker_client.api.build(
                        path=str(data_file_path.parents[0].resolve()),
                        rm=True, tag=image, pull=True, forcerm=True
                ):
                    response.append(line.decode("utf-8"))
                    logger.info(line.decode("utf-8"))

                logger.info("Docker image %s built.", image)
                docker_config["image"] = image
                docker_config["privileged"] = False
                if rm_image:
                    self.docker_client.images.remove(orig_image)
            elif image:
                docker_config["image"] = image
                if image not in str(self.docker_client.images.list()):
                    logger.info("Pulling %s docker image! "
                                "This can take a while depending on your connection.",
                                image
                                )
                    if IS_INTERACTIVE:
                        print("Pulling %s : ",  image, end="")
                    for _ in self.docker_client.api.pull(
                            image, stream=True, decode=True
                    ):
                        if IS_INTERACTIVE:
                            print("#", end="")
                    if IS_INTERACTIVE:
                        print("  [SUCCESS]")
                logger.info("Image pulled!")

            if cmd:
                docker_config["command"] = cmd

            try:
                logger.info(
                    "Running %s docker container!",
                    image
                )
                container = self.docker_client.containers.run(**docker_config)
            except (HTTPError, APIError) as exception:
                docker_cli_command = "docker run -d "
                environment = docker_config.get("environment")
                volumes = docker_config.get("volumes")
                ports = docker_config.get("ports")
                name = docker_config.get("name")
                command = docker_config.get("command")
                if volumes:
                    for k, v in volumes.items():
                        docker_cli_command += f" -v {k}:{v}"
                if ports:
                    for k, v in ports.items():
                        docker_cli_command += f" -p {k}:{v}"
                if environment:
                    docker_cli_command += " -e " + " -e ".join(environment)
                if name:
                    docker_cli_command += " --name " + name
                docker_cli_command += " " + image
                if command:
                    docker_cli_command += " " + " ".join(command)

                logger.info(
                    "Failed to run %s docker container!\nDocker command:\n" \
                    "cd %s\n" \
                    "%s\n",
                    image,
                    self.working_directory,
                    docker_cli_command
                )
                raise APIError(
                    "Failed to run %s docker container!\nDocker command:\ncd %s\n%s\n" %
                    (image,
                    self.working_directory,
                    docker_cli_command)
                ) from exception
            # wait for data to load
            time.sleep(4)
            self.storages[data_source_name][storage_type]["container"] = container

        if container.status != "running":
            container.start()

        time.sleep(4)
        logger.info("Started %s docker container!", image)
        self.containers.add(container.id)
        port = int([p[0]["HostPort"] for p in container.attrs.get(
            "HostConfig"
        ).get("PortBindings").values()][0])
        self.storages[data_source_name][storage_type]["endpoint"] = \
            self.storages[data_source_name]["backend"].get_endpoint(port)
        logger.info(
            "Docker container is running:\n\tcontainer name: %s\n\tdata source: %s\n\tendpoint: %s",
            container_name,
            data_source_name,
            self.storages[data_source_name][storage_type]["endpoint"]
        )

    def get_endpoint(self, data_source_name, storage_type):
        """

        Args:
            data_source_name:
            storage_type:

        Returns:

        """
        return self.storages[data_source_name][storage_type]["endpoint"]

    def close(self):
        """

        """
        instances = self.get_instances()
        keep_container = set(c for i in instances for c in i.containers if i != self)
        for container_id in self.containers:
            if container_id not in keep_container:
                try:
                    container = self.docker_client.containers.get(container_id)
                    container.stop()
                except AttributeError:
                    pass
        try:
            self.docker_client.close()
        except TypeError:
            pass


def stop_containers():
    """ Stop containers on exit"""
    for instance in Storage.get_instances():
        for container_id in instance.containers:
            try:
                container = instance.docker_client.containers.get(container_id)
                container.stop()
            except AttributeError:
                pass


# Execute on python exit.
atexit.register(stop_containers)
