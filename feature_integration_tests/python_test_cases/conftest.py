import logging
import subprocess

import docker as pypi_docker
import pytest

logger = logging.getLogger(__name__)


# Override for the docker fixture from itf/plugin as scope is set to function in original
# Tests here are verifying that the data is stored persistently after program is closed,
# so we need to have the container available for the whole class scope.
@pytest.fixture(scope="class")
def docker(request):
    docker_image_bootstrap = request.config.getoption("docker_image_bootstrap")
    if docker_image_bootstrap:
        logger.info(
            f"Executing custom image bootstrap command: {docker_image_bootstrap}"
        )
        subprocess.run([docker_image_bootstrap], check=True)

    docker_image = request.config.getoption("docker_image")
    client = pypi_docker.from_env()
    container = client.containers.run(
        docker_image, "sleep infinity", detach=True, auto_remove=True, init=True
    )
    yield container
    container.stop(timeout=1)


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "PartiallyVerifies: Requirement partially verified by the test"
    )
    config.addinivalue_line(
        "markers", "FullyVerifies: Requirement fully verified by the test"
    )
    config.addinivalue_line("markers", "Description: Description of the test")
    config.addinivalue_line("markers", "TestType: Type of the test")
    config.addinivalue_line(
        "markers", "DerivationTechnique: Technique used for test derivation"
    )
    config.addinivalue_line("addopts", "--junit-xml=junit.xml")


def pytest_collection_modifyitems(session, config, items):
    """Modify collected test items to add custom markers as user properties.
    This allows parsing xml report to Sphinx objects and reporting test results."""
    for item in items:
        for marker in item.iter_markers():
            name = marker.name
            value = marker.args
            item.user_properties.append((name, value))
