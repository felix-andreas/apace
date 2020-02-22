from click.testing import CliRunner
from apace.cli import cli


def test_twiss():
    runner = CliRunner()
    result = runner.invoke(cli, ["twiss"])
    assert result.exit_code == 0
    assert result.output == "Test\n"
