from pathlib import Path
from click.testing import CliRunner
from apace.cli import cli

BASE_PATH = Path(__file__).resolve().parent
FODO_PATH = BASE_PATH / "data/lattices/fodo_ring.json"


def test_twiss(tmp_path):
    runner = CliRunner()
    out_path = tmp_path / "test_twiss.pdf"
    result = runner.invoke(cli, ["twiss", str(FODO_PATH), "--output", out_path])
    assert result.exit_code == 0
