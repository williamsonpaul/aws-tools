"""
Command line interface for AcronymCreator.
"""

import csv
import io
import json
import yaml
import tomli_w
import click
from .core import AcronymCreator, AcronymOptions

# Trigger CI build


@click.command()
@click.argument("phrase", required=True)
@click.option(
    "--include-articles",
    is_flag=True,
    default=False,
    help="Include articles (a, an, the) in the acronym",
)
@click.option(
    "--min-length",
    type=int,
    default=2,
    help="Minimum word length to include (default: 2)",
)
@click.option("--max-words", type=int, help="Maximum number of words to process")
@click.option(
    "--lowercase", is_flag=True, default=False, help="Output acronym in lowercase"
)
@click.option(
    "--format",
    type=click.Choice(
        ["text", "json", "yaml", "csv", "tsv", "toml"], case_sensitive=False
    ),
    default="text",
    help="Output format (default: text)",
)
@click.version_option(version="0.1.0", prog_name="acronymcreator")
def main(phrase, include_articles, min_length, max_words, lowercase, format):
    """Generate acronyms from phrases.

    PHRASE: The phrase to create an acronym from

    Examples:

        acronymcreator "The Quick Brown Fox"

        acronymcreator "Application Programming Interface" --include-articles

        acronymcreator "Very Long Phrase With Many Words" --max-words 3
    """
    creator = AcronymCreator()
    options = AcronymOptions(
        include_articles=include_articles,
        min_word_length=min_length,
        max_words=max_words,
        force_uppercase=not lowercase,
    )

    result = creator.create_basic_acronym(phrase, options)

    if not result:
        click.echo("No acronym could be generated from the given phrase.", err=True)
        raise click.Abort()

    if format == "json":
        output = {
            "phrase": phrase,
            "acronym": result,
            "options": {
                "include_articles": include_articles,
                "min_word_length": min_length,
                "max_words": max_words,
                "lowercase": lowercase,
            },
        }
        click.echo(json.dumps(output, indent=2))
    elif format == "yaml":
        output = {
            "phrase": phrase,
            "acronym": result,
            "options": {
                "include_articles": include_articles,
                "min_word_length": min_length,
                "max_words": max_words,
                "lowercase": lowercase,
            },
        }
        click.echo(yaml.dump(output, default_flow_style=False))
    elif format == "csv":
        output_buffer = io.StringIO()
        csv_writer = csv.writer(output_buffer)
        # Write header
        csv_writer.writerow(
            [
                "phrase",
                "acronym",
                "include_articles",
                "min_word_length",
                "max_words",
                "lowercase",
            ]
        )
        # Write data row
        csv_writer.writerow(
            [
                phrase,
                result,
                str(include_articles).lower(),
                min_length,
                max_words if max_words is not None else "",
                str(lowercase).lower(),
            ]
        )
        click.echo(output_buffer.getvalue().rstrip())
    elif format == "tsv":
        output_buffer = io.StringIO()
        tsv_writer = csv.writer(output_buffer, delimiter="\t")
        # Write header
        tsv_writer.writerow(
            [
                "phrase",
                "acronym",
                "include_articles",
                "min_word_length",
                "max_words",
                "lowercase",
            ]
        )
        # Write data row
        tsv_writer.writerow(
            [
                phrase,
                result,
                str(include_articles).lower(),
                min_length,
                max_words if max_words is not None else "",
                str(lowercase).lower(),
            ]
        )
        click.echo(output_buffer.getvalue().rstrip())
    elif format == "toml":
        output = {
            "phrase": phrase,
            "acronym": result,
            "include_articles": include_articles,
            "min_word_length": min_length,
            "max_words": max_words if max_words is not None else "",
            "lowercase": lowercase,
        }
        click.echo(tomli_w.dumps(output).rstrip())
    else:
        click.echo(result)


if __name__ == "__main__":
    main()
