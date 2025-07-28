import pytest


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
    config.addinivalue_line(
        "addopts", "--junit-xml=/home/pko/qorix/fit_example/junit.xml"
    )


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        for marker in item.iter_markers():
            name = marker.name
            value = marker.args
            # if name == "req":
            #     item.user_properties.append((name, value[0]))
            # else:
            item.user_properties.append((name, value))
