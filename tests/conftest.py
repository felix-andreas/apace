import pytest
import json
from pathlib import Path
import apace as ap

BASE_PATH = Path(__file__).resolve().parent
LATTICE_PATH = BASE_PATH / "../data/lattices"
FODO_RING_JSON = json.loads((LATTICE_PATH / "fodo_ring.json").read_text())


def pytest_addoption(parser):
    parser.addoption(
        "--plots", action="store_true", default=False, help="Plot test results"
    )


@pytest.fixture
def plots(request):
    return request.config.getoption("--plots")


@pytest.fixture
def base_path():
    return BASE_PATH


@pytest.fixture
def lattice_path():
    return LATTICE_PATH


@pytest.fixture
def fodo_ring():
    return ap.Lattice.from_dict(FODO_RING_JSON)
