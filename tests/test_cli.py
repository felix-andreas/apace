from click.testing import CliRunner
from apace.cli import cli


def test_twiss(tmp_path, lattice_path):
    runner = CliRunner()
    input_path = str(lattice_path / "fodo_cell.json")
    output_path = tmp_path / "test_twiss.pdf"
    result = runner.invoke(cli, ["twiss", input_path, "--output", output_path])
    assert result.exit_code == 0
