"""tests/unit/test_cli.py"""

from __future__ import annotations

from click.testing import CliRunner

from datasets.cli import main


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_catalog_list(tmp_path):
    import yaml

    entry = {
        "name": "test-bench",
        "source": "harbor",
        "source_url": "https://example.com",
        "task_count": 10,
        "domain": ["test"],
        "difficulty_profile": "easy",
        "format": "harbor",
        "applicability": "Testing only.",
    }
    (tmp_path / "test.yaml").write_text(yaml.dump(entry))

    runner = CliRunner()
    result = runner.invoke(main, ["catalog", "list", "--catalog-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "test-bench" in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "recommend" in result.output or "catalog" in result.output
