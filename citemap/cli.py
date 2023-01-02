import os

from pathlib import Path
from . import citations_mapper
import rich_click as click


# CLI app configuration
@click.command()
@click.option("--author-id", help="Your google scholar author id. For example, "
                                  "if your URL is https://scholar.google.com/citations?user=WGggocoAAAAJ&hl=en, "
                                  "then your author_id is the  part after user= and before &hl=en, i.e., WGggocoAAAAJ")
@click.option("--serp-api-token", envvar="SERP_API_TOKEN", default=None, help="Your serp api token")
@click.option("--output-dir", help="The directory to save the outputs", default=Path(os.getcwd()), show_default=True)
def cli(author_id, serp_api_token, output_dir):
    """A small python app to generate and plot your Google Scholar citations."""
    citations_mapper(author_id, serp_api_token, output_dir)

