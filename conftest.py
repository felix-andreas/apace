import json
from pathlib import Path

import pytest

import apace as ap


# use @pytest.mark.slow to skip slow tests
# for more information see: https://docs.pytest.org/en/latest/example/simple.html
def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--plots", action="store_true", default=False, help="Plot test results"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture
def plots(request):
    return request.config.getoption("--plots")


BASE_PATH = Path(__file__).parent
TESTS_DIR = BASE_PATH / "tests"
LATTICE_PATH = BASE_PATH / "data/lattices"
FODO_CELL_JSON = json.loads((LATTICE_PATH / "fodo_cell.json").read_text())
NESTED_LATTICE = json.loads((LATTICE_PATH / "nested_lattice.json").read_text())


@pytest.fixture
def base_path():
    return BASE_PATH


@pytest.fixture
def lattice_path():
    return LATTICE_PATH


@pytest.fixture
def test_output_dir():
    path = TESTS_DIR / "_test_output"
    path.mkdir(exist_ok=True)
    return path


@pytest.fixture
def fodo_cell():
    return ap.Lattice.from_dict(FODO_CELL_JSON)


# TODO: use fodo_cell where possible! (for faster tests)
@pytest.fixture
def fodo_ring(fodo_cell):
    return ap.Lattice("fodo-ring", 8 * [fodo_cell])


@pytest.fixture
def nested_lattice():
    return ap.Lattice.from_dict(NESTED_LATTICE)
