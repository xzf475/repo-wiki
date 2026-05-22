from click.testing import CliRunner

from indexer.cli import main


def test_agent_capabilities_cli_outputs_contract():
    result = CliRunner().invoke(main, ["agent", "capabilities"])

    assert result.exit_code == 0
    assert '"local_and_remote": true' in result.output
    assert "post_edit_verify_tool" in result.output


def test_agent_schema_cli_outputs_openapi_contract():
    result = CliRunner().invoke(main, ["agent", "schema"])

    assert result.exit_code == 0
    assert '"openapi": "3.1.0"' in result.output
    assert "/post-edit-verify" in result.output


def test_agent_context_cli_requires_symbol_id():
    result = CliRunner().invoke(main, ["agent", "context"])

    assert result.exit_code != 0
    assert "Missing option" in result.output
