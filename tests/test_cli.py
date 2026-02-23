"""
Tests for the CLI module.
"""

import csv
import io
import json
import tomllib
from click.testing import CliRunner
from src.acronymcreator.cli import main


class TestCLI:
    """Test cases for the CLI interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_basic_acronym(self):
        """Test basic CLI functionality."""
        result = self.runner.invoke(main, ["Hello World"])
        assert result.exit_code == 0
        assert result.output.strip() == "HW"

    def test_cli_with_articles_excluded(self):
        """Test CLI with articles excluded by default."""
        result = self.runner.invoke(main, ["The Quick Brown Fox"])
        assert result.exit_code == 0
        assert result.output.strip() == "QBF"

    def test_cli_with_articles_included(self):
        """Test CLI with articles included."""
        result = self.runner.invoke(main, ["The Quick Brown Fox", "--include-articles"])
        assert result.exit_code == 0
        assert result.output.strip() == "TQBF"

    def test_cli_lowercase_output(self):
        """Test CLI with lowercase output."""
        result = self.runner.invoke(main, ["hello world", "--lowercase"])
        assert result.exit_code == 0
        assert result.output.strip() == "hw"

    def test_cli_empty_phrase(self):
        """Test CLI with empty phrase that produces no result."""
        result = self.runner.invoke(main, [""])
        assert result.exit_code == 1
        assert "No acronym could be generated" in result.output

    def test_cli_help(self):
        """Test CLI help output."""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Generate acronyms from phrases" in result.output
        assert "PHRASE" in result.output

    def test_cli_version(self):
        """Test CLI version output."""
        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_json_output(self):
        """Test CLI with JSON output format."""
        result = self.runner.invoke(main, ["Hello World", "--format", "json"])
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["phrase"] == "Hello World"
        assert output["acronym"] == "HW"
        assert "options" in output

    def test_cli_json_output_with_options(self):
        """Test CLI with JSON output and various options."""
        result = self.runner.invoke(
            main,
            [
                "The Quick Brown Fox",
                "--format",
                "json",
                "--include-articles",
                "--min-length",
                "1",
            ],
        )
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["phrase"] == "The Quick Brown Fox"
        assert output["acronym"] == "TQBF"
        assert output["options"]["include_articles"] is True
        assert output["options"]["min_word_length"] == 1

    def test_cli_yaml_output(self):
        """Test CLI with YAML output format."""
        result = self.runner.invoke(main, ["Hello World", "--format", "yaml"])
        assert result.exit_code == 0
        assert "phrase: Hello World" in result.output
        assert "acronym: HW" in result.output
        assert "options:" in result.output

    def test_cli_yaml_output_with_options(self):
        """Test CLI with YAML output and various options."""
        result = self.runner.invoke(
            main,
            [
                "The Quick Brown Fox",
                "--format",
                "yaml",
                "--include-articles",
                "--lowercase",
            ],
        )
        assert result.exit_code == 0
        assert "phrase: The Quick Brown Fox" in result.output
        assert "acronym: tqbf" in result.output
        assert "include_articles: true" in result.output
        assert "lowercase: true" in result.output

    def test_cli_csv_output_basic(self):
        """Test CLI with CSV output format."""
        result = self.runner.invoke(main, ["Hello World", "--format", "csv"])
        assert result.exit_code == 0

        # Parse CSV output
        csv_reader = csv.DictReader(io.StringIO(result.output))
        rows = list(csv_reader)

        assert len(rows) == 1
        assert rows[0]["phrase"] == "Hello World"
        assert rows[0]["acronym"] == "HW"
        assert rows[0]["include_articles"] == "false"
        assert rows[0]["min_word_length"] == "2"
        assert rows[0]["max_words"] == ""
        assert rows[0]["lowercase"] == "false"

    def test_cli_csv_output_with_articles(self):
        """Test CLI with CSV output and include-articles option."""
        result = self.runner.invoke(
            main, ["The Quick Brown Fox", "--format", "csv", "--include-articles"]
        )
        assert result.exit_code == 0

        # Parse CSV output
        csv_reader = csv.DictReader(io.StringIO(result.output))
        rows = list(csv_reader)

        assert len(rows) == 1
        assert rows[0]["phrase"] == "The Quick Brown Fox"
        assert rows[0]["acronym"] == "TQBF"
        assert rows[0]["include_articles"] == "true"
        assert rows[0]["min_word_length"] == "2"
        assert rows[0]["lowercase"] == "false"

    def test_cli_csv_output_lowercase(self):
        """Test CLI with CSV output and lowercase option."""
        result = self.runner.invoke(
            main, ["Hello World", "--format", "csv", "--lowercase"]
        )
        assert result.exit_code == 0

        # Parse CSV output
        csv_reader = csv.DictReader(io.StringIO(result.output))
        rows = list(csv_reader)

        assert len(rows) == 1
        assert rows[0]["acronym"] == "hw"
        assert rows[0]["lowercase"] == "true"

    def test_cli_csv_output_all_options(self):
        """Test CLI with CSV output and all options."""
        result = self.runner.invoke(
            main,
            [
                "The Quick Brown Fox Jumps",
                "--format",
                "csv",
                "--include-articles",
                "--lowercase",
                "--min-length",
                "3",
                "--max-words",
                "3",
            ],
        )
        assert result.exit_code == 0

        # Parse CSV output
        csv_reader = csv.DictReader(io.StringIO(result.output))
        rows = list(csv_reader)

        assert len(rows) == 1
        assert rows[0]["phrase"] == "The Quick Brown Fox Jumps"
        assert rows[0]["include_articles"] == "true"
        assert rows[0]["min_word_length"] == "3"
        assert rows[0]["max_words"] == "3"
        assert rows[0]["lowercase"] == "true"

    def test_cli_csv_output_special_characters(self):
        """Test CLI with CSV output handling special characters."""
        result = self.runner.invoke(main, ['Hello, World! "Test"', "--format", "csv"])
        assert result.exit_code == 0

        # Parse CSV output - CSV library should handle special characters
        csv_reader = csv.DictReader(io.StringIO(result.output))
        rows = list(csv_reader)

        assert len(rows) == 1
        assert rows[0]["acronym"] == "HWT"

    def test_cli_csv_output_header_structure(self):
        """Test CSV header structure matches expected columns."""
        result = self.runner.invoke(main, ["Test Phrase", "--format", "csv"])
        assert result.exit_code == 0

        lines = result.output.strip().split("\n")
        header = lines[0]

        # Check that header contains all expected columns
        expected_columns = [
            "phrase",
            "acronym",
            "include_articles",
            "min_word_length",
            "max_words",
            "lowercase",
        ]
        for column in expected_columns:
            assert column in header

    def test_cli_tsv_output_basic(self):
        """Test CLI with TSV output format."""
        result = self.runner.invoke(main, ["Hello World", "--format", "tsv"])
        assert result.exit_code == 0

        # Parse TSV output
        tsv_reader = csv.DictReader(io.StringIO(result.output), delimiter="\t")
        rows = list(tsv_reader)

        assert len(rows) == 1
        assert rows[0]["phrase"] == "Hello World"
        assert rows[0]["acronym"] == "HW"
        assert rows[0]["include_articles"] == "false"
        assert rows[0]["min_word_length"] == "2"
        assert rows[0]["max_words"] == ""
        assert rows[0]["lowercase"] == "false"

    def test_cli_tsv_output_with_articles(self):
        """Test CLI with TSV output and include-articles option."""
        result = self.runner.invoke(
            main, ["The Quick Brown Fox", "--format", "tsv", "--include-articles"]
        )
        assert result.exit_code == 0

        # Parse TSV output
        tsv_reader = csv.DictReader(io.StringIO(result.output), delimiter="\t")
        rows = list(tsv_reader)

        assert len(rows) == 1
        assert rows[0]["phrase"] == "The Quick Brown Fox"
        assert rows[0]["acronym"] == "TQBF"
        assert rows[0]["include_articles"] == "true"
        assert rows[0]["min_word_length"] == "2"
        assert rows[0]["lowercase"] == "false"

    def test_cli_tsv_output_lowercase(self):
        """Test CLI with TSV output and lowercase option."""
        result = self.runner.invoke(
            main, ["Hello World", "--format", "tsv", "--lowercase"]
        )
        assert result.exit_code == 0

        # Parse TSV output
        tsv_reader = csv.DictReader(io.StringIO(result.output), delimiter="\t")
        rows = list(tsv_reader)

        assert len(rows) == 1
        assert rows[0]["acronym"] == "hw"
        assert rows[0]["lowercase"] == "true"

    def test_cli_tsv_output_all_options(self):
        """Test CLI with TSV output and all options."""
        result = self.runner.invoke(
            main,
            [
                "The Quick Brown Fox Jumps",
                "--format",
                "tsv",
                "--include-articles",
                "--lowercase",
                "--min-length",
                "3",
                "--max-words",
                "3",
            ],
        )
        assert result.exit_code == 0

        # Parse TSV output
        tsv_reader = csv.DictReader(io.StringIO(result.output), delimiter="\t")
        rows = list(tsv_reader)

        assert len(rows) == 1
        assert rows[0]["phrase"] == "The Quick Brown Fox Jumps"
        assert rows[0]["include_articles"] == "true"
        assert rows[0]["min_word_length"] == "3"
        assert rows[0]["max_words"] == "3"
        assert rows[0]["lowercase"] == "true"

    def test_cli_tsv_output_special_characters(self):
        """Test CLI with TSV output handling special characters."""
        result = self.runner.invoke(main, ['Hello, World! "Test"', "--format", "tsv"])
        assert result.exit_code == 0

        # Parse TSV output - CSV library should handle special characters
        tsv_reader = csv.DictReader(io.StringIO(result.output), delimiter="\t")
        rows = list(tsv_reader)

        assert len(rows) == 1
        assert rows[0]["acronym"] == "HWT"

    def test_cli_tsv_output_header_structure(self):
        """Test TSV header structure matches expected columns."""
        result = self.runner.invoke(main, ["Test Phrase", "--format", "tsv"])
        assert result.exit_code == 0

        lines = result.output.strip().split("\n")
        header = lines[0]

        # Check that header contains all expected columns with tab separators
        expected_columns = [
            "phrase",
            "acronym",
            "include_articles",
            "min_word_length",
            "max_words",
            "lowercase",
        ]
        for column in expected_columns:
            assert column in header

        # Verify tab delimiter is used
        assert "\t" in header

    def test_cli_tsv_output_with_commas(self):
        """Test TSV output properly handles phrases with commas."""
        result = self.runner.invoke(
            main, ["Hello, Wonderful, Amazing World", "--format", "tsv"]
        )
        assert result.exit_code == 0

        # Parse TSV output
        tsv_reader = csv.DictReader(io.StringIO(result.output), delimiter="\t")
        rows = list(tsv_reader)

        assert len(rows) == 1
        # Verify the entire phrase is preserved with commas
        assert rows[0]["phrase"] == "Hello, Wonderful, Amazing World"

    def test_cli_tsv_output_with_tabs_in_phrase(self):
        """Test TSV output properly handles phrases with tab characters."""
        result = self.runner.invoke(main, ["Hello\tWorld", "--format", "tsv"])
        assert result.exit_code == 0

        # Parse TSV output - CSV library should properly escape tabs
        tsv_reader = csv.DictReader(io.StringIO(result.output), delimiter="\t")
        rows = list(tsv_reader)

        assert len(rows) == 1
        # Verify the entire phrase is preserved with tab
        assert "Hello" in rows[0]["phrase"] and "World" in rows[0]["phrase"]

    def test_cli_toml_output_basic(self):
        """Test CLI with TOML output format."""
        result = self.runner.invoke(main, ["Hello World", "--format", "toml"])
        assert result.exit_code == 0

        # Parse TOML output
        output = tomllib.loads(result.output)

        assert output["phrase"] == "Hello World"
        assert output["acronym"] == "HW"
        assert output["include_articles"] is False
        assert output["min_word_length"] == 2
        assert output["max_words"] == ""
        assert output["lowercase"] is False

    def test_cli_toml_output_with_articles(self):
        """Test CLI with TOML output and include-articles option."""
        result = self.runner.invoke(
            main, ["The Quick Brown Fox", "--format", "toml", "--include-articles"]
        )
        assert result.exit_code == 0

        # Parse TOML output
        output = tomllib.loads(result.output)

        assert output["phrase"] == "The Quick Brown Fox"
        assert output["acronym"] == "TQBF"
        assert output["include_articles"] is True
        assert output["min_word_length"] == 2
        assert output["lowercase"] is False

    def test_cli_toml_output_lowercase(self):
        """Test CLI with TOML output and lowercase option."""
        result = self.runner.invoke(
            main, ["Hello World", "--format", "toml", "--lowercase"]
        )
        assert result.exit_code == 0

        # Parse TOML output
        output = tomllib.loads(result.output)

        assert output["acronym"] == "hw"
        assert output["lowercase"] is True

    def test_cli_toml_output_all_options(self):
        """Test CLI with TOML output and all options."""
        result = self.runner.invoke(
            main,
            [
                "The Quick Brown Fox Jumps",
                "--format",
                "toml",
                "--include-articles",
                "--lowercase",
                "--min-length",
                "3",
                "--max-words",
                "3",
            ],
        )
        assert result.exit_code == 0

        # Parse TOML output
        output = tomllib.loads(result.output)

        assert output["phrase"] == "The Quick Brown Fox Jumps"
        assert output["include_articles"] is True
        assert output["min_word_length"] == 3
        assert output["max_words"] == 3
        assert output["lowercase"] is True

    def test_cli_toml_output_types(self):
        """Test CLI with TOML output validates correct types."""
        result = self.runner.invoke(
            main,
            [
                "Test Phrase",
                "--format",
                "toml",
                "--include-articles",
                "--min-length",
                "5",
                "--max-words",
                "10",
            ],
        )
        assert result.exit_code == 0

        # Parse TOML output
        output = tomllib.loads(result.output)

        # Verify types
        assert isinstance(output["phrase"], str)
        assert isinstance(output["acronym"], str)
        assert isinstance(output["include_articles"], bool)
        assert isinstance(output["min_word_length"], int)
        assert isinstance(output["max_words"], int)
        assert isinstance(output["lowercase"], bool)

    def test_cli_toml_output_special_characters(self):
        """Test CLI with TOML output handling special characters."""
        result = self.runner.invoke(main, ['Hello, World! "Test"', "--format", "toml"])
        assert result.exit_code == 0

        # Parse TOML output - should handle special characters correctly
        output = tomllib.loads(result.output)

        assert output["phrase"] == 'Hello, World! "Test"'
        assert output["acronym"] == "HWT"
