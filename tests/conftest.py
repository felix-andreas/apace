import json
from pathlib import Path

import pytest

import apace as ap

BASE_PATH = Path(__file__).resolve().parent
LATTICE_PATH = BASE_PATH / "../data/lattices"
FODO_CELL_JSON = json.loads((LATTICE_PATH / "fodo_cell.json").read_text())


@pytest.fixture
def base_path():
    return BASE_PATH


@pytest.fixture
def lattice_path():
    return LATTICE_PATH


@pytest.fixture
def fodo_cell():
    return ap.Lattice.from_dict(FODO_CELL_JSON)


# Todo: use fodo_cell where possible! (for faster tests)
@pytest.fixture
def fodo_ring(fodo_cell):
    return ap.Lattice("fodo-ring", 8 * [fodo_cell])
