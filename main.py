import os
from typing import Dict
from openpyxl.workbook import Workbook
from serpapi import GoogleScholarSearch, GoogleSearch
import logging
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(show_path=False)]
)
log = logging.getLogger("rich")
console = Console

# TODO: Create commandline args for author_id, api_key_env_name, output_dir, etc.
if __name__ == "__main__":
    user_info_search_param: Dict = {
        "engine": "google_scholar_author",
        "author_id": "WGggocoAAAAJ",
        "api_key": os.getenv("SERP_API_KEY"),
        "num": 100
    }
    search = GoogleScholarSearch(user_info_search_param)
    results = search.get_dict()
    log.info("Found {num_papers} articles".format(num_papers=len(results['articles'])))

    # Create a xls workbook to store some additional information
    citations_summary = Workbook()
    ws = citations_summary.active

    table = Table(title="Citation Summary")

    table.add_column("Article Title")
    table.add_column("Article Link", style="cyan")
    table.add_column("Article Year")
    table.add_column("Article Citation Count", style='magenta')
    table.add_column("citation_title")
    table.add_column("citer_name")
    table.add_column("citer_email")
    table.add_column("citer_affiliation")
    table.add_column("citer_webpage")

    try:
        for article in results['articles']:
            # Get the paper ID
            article_title = article['title']
            article__link = article['title']
            article__year = article['year']
            article_cites = article['cited_by']['value']
            offset: int = 0
            num_results: int = 20
            results_have_more_pages: bool = True
            while results_have_more_pages:
                cites_id = article["cited_by"]["cites_id"]
                log.info("Processing {paper} :: Cited by {cite_count}".format(
                    paper=article["title"], cite_count=article['cited_by']['value']))

                cited_by_param: Dict = {
                    "api_key": os.getenv('SERP_API_KEY'),
                    "engine": "google_scholar",
                    "hl": "en",
                    "cites": cites_id,
                    "num": num_results,
                    "start": offset
                }

                search_result = GoogleSearch(cited_by_param).get_dict()
                # Check to see if there are more pages to look through. If no more results, break.
                if search_result['search_information']['organic_results_state'] == "Fully empty":
                    results_have_more_pages = False
                    break
                else:
                    offset += 20
                    organic_results: Dict = search_result["organic_results"]

                    for citation in organic_results:
                        citation_title = citation['title']
                        citation__link = citation['link']
                        try:
                            authors = citation['publication_info']['authors']
                            for author in authors:
                                author_id = author['author_id']
                                author_info_search_param: Dict = {
                                    "engine": "google_scholar_author",
                                    "author_id": author_id,
                                    "api_key": os.getenv("SERP_API_KEY"),
                                }
                                author_info_search = GoogleScholarSearch(
                                    author_info_search_param).get_dict().__getitem__("author")
                                author_name = author_info_search.__getitem__("name")
                                try:
                                    author_email = author_info_search.__getitem__("email")
                                except Exception:
                                    author_email = None
                                try:
                                    author_webpage = author_info_search.__getitem__("website")
                                except Exception:
                                    author_webpage = None
                                try:
                                    author_affiliation = author_info_search.__getitem__("affiliations")
                                except Exception:
                                    author_affiliation = None

                                ws.append([article_title, article__link, article__year, article_cites, citation_title,
                                           citation__link, author_name, author_email, author_affiliation,
                                           author_webpage])
                                table.add_row(article_title, article__link, str(article__year), str(article_cites),
                                              citation_title, citation__link, author_name, author_email,
                                              author_affiliation, author_webpage)
                        except KeyError:
                            continue

    except:
        # Save citation summary
        # TODO: Save location from input cli args
        console.print(table)
        citations_summary.save("Citation Summary.xlsx")

    console.print(table)
    citations_summary.save("Citation Summary.xlsx")
