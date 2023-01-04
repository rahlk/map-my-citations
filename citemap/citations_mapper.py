import os
from typing import Dict
from openpyxl.workbook import Workbook
from serpapi import GoogleScholarSearch, GoogleSearch
import logging
from rich.logging import RichHandler
import pandas as pd
import plotly.express as px
from ip2geotools.databases.noncommercial import DbIpCity

# NOTE: SERP API prints some console output. This is help redirect all that junk to /dev/null.
import contextlib
import socket as sock
from pathlib import Path

# Rich progress bar configuration
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)

# Define custom progress bar
progress_bar = Progress(
    SpinnerColumn(),
    TextColumn("•"),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    TextColumn("• Completed/Total:"),
    MofNCompleteColumn(),
    TextColumn("• Elapsed:"),
    TimeElapsedColumn(),
    TextColumn("• Remaining:"),
    TimeRemainingColumn()
)

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(show_path=False)]
)
log = logging.getLogger("rich")


# CLI app configuration

def get_geoloc(google_scholar_url: str) -> tuple[str, str, str, float, float]:
    """
    Get the geographic location of the author using their verified Google Scholar email address
    :param google_scholar_url: The author's verified Google Scholar email address
    :return: a tuple of the author's (country, region, city, latitude, longitude)
    """
    country, region, city, lat, long = None, None, None, None, None
    try:
        with open(os.devnull, 'w') as null, contextlib.redirect_stdout(null), contextlib.redirect_stderr(null):
            details = DbIpCity.get(sock.gethostbyname(google_scholar_url), api_key='free')
            country: str = details.country
            region: str = details.region
            city: str = details.city
            lat: float = float(details.latitude)
            long: float = float(details.longitude)
    except sock.gaierror:
        pass
    return country, region, city, lat, long


def plot_geoloc(map_data: pd.DataFrame, output_directory: Path) -> None:
    """
    Plot the map data into a file
    :param map_data: A DataFrame of the map data.
    :param output_directory: A directory to save the map.
    """
    fig = px.scatter_mapbox(map_data, lat="lat", lon="long", hover_name="city",
                            hover_data=["citing_author", "citing_paper", "citing_paper_link",
                                        "cited_paper", "cited_paper_link"], zoom=2)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.write_html(output_directory.joinpath("citation_map.html"))


def citations_mapper(author_id: str, serp_api_token: str, output_dir: Path):
    user_info_search_param: Dict = {
        "engine": "google_scholar_author",
        "author_id": author_id,
        "api_key": serp_api_token,
        "num": 100
    }
    with open(os.devnull, 'w') as null, contextlib.redirect_stdout(null), contextlib.redirect_stderr(null):
        search = GoogleScholarSearch(user_info_search_param)
        results = search.get_dict()

    log.info("Found {num_papers} articles".format(num_papers=len(results['articles'])))

    # Create a xls workbook to store some additional information
    citations_summary = Workbook()
    worksheet = citations_summary.active

    map_coord = []

    try:
        with progress_bar as p:
            for article in p.track(results['articles'], total=len(results['articles'])):
                # Get the paper ID
                article_title = article['title']
                article__link = article['link']
                article__year = article['year']
                article_cites = article['cited_by']['value']
                offset: int = 0
                num_results: int = 20
                results_have_more_pages: bool = True
                log.info("Processing {paper} :: Cited by {cite_count}".format(
                    paper=article["title"], cite_count=article['cited_by']['value']))
                if article_cites == 0 or article['cited_by']['value'] is None:
                    log.info("No citations for this paper. Skipping...")
                    continue

                while results_have_more_pages:
                    cites_id = article.get("cited_by").get("cites_id")
                    if cites_id is None:
                        continue

                    cited_by_param: Dict = {
                        "api_key": os.getenv('SERP_API_KEY'),
                        "engine": "google_scholar",
                        "hl": "en",
                        "cites": cites_id,
                        "num": num_results,
                        "start": offset
                    }

                    with open(os.devnull, 'w') as null, contextlib.redirect_stdout(null), contextlib.redirect_stderr(
                            null):
                        search_result = GoogleSearch(cited_by_param).get_dict()
                    # Check to see if there are more pages to look through. If no more results, break.
                    if 'search_information' not in search_result:
                        results_have_more_pages = False
                        break
                    elif search_result['search_information']['organic_results_state'] == "Fully empty":
                        results_have_more_pages = False
                        break
                    else:
                        offset += 20
                        organic_results: Dict = search_result["organic_results"]

                        for citation in organic_results:
                            citation_title = citation['title']

                            # Citation link (
                            citation__link = citation.get('link')

                            authors = citation.get('publication_info').get('authors')

                            if authors is None:
                                continue

                            for author in authors:
                                author_id = author['author_id']
                                author_info_search_param: Dict = {
                                    "engine": "google_scholar_author",
                                    "author_id": author_id,
                                    "api_key": serp_api_token,
                                }
                                with open(os.devnull, 'w') as null, \
                                        contextlib.redirect_stdout(null), contextlib.redirect_stderr(null):
                                    author_info_search = GoogleScholarSearch(
                                        author_info_search_param).get_dict().get("author")

                                author_name = author_info_search.get("name")
                                author_email = author_info_search.get("email").split(" ")[-1]
                                author_loc_country, author_loc_region, author_loc_city, \
                                    author_loc_lat, author_loc_long = get_geoloc(author_email)
                                author_webpage = author_info_search.get("website")
                                author_affiliation = author_info_search.get("affiliations")

                                # Add row to excel worksheet
                                worksheet.append([
                                    # Article Information
                                    article_title, article__link, article__year, article_cites,
                                    citation_title, citation__link, author_name, author_email,
                                    # Latitude and longitude information
                                    author_loc_lat, author_loc_long,
                                    # Citer Information
                                    author_loc_country, author_loc_region, author_loc_city,
                                    author_affiliation, author_webpage])

                                # Populate geolocation coordinates list for mapping
                                if (author_loc_lat is not None) and (author_loc_long is not None):
                                    map_coord.append(
                                        (author_loc_lat, author_loc_long, author_loc_city, citation_title,
                                         author_name, citation__link, article_title, article__link))

    finally:
        map_data = pd.DataFrame(map_coord,
                                columns=["lat", "long", "city", "citing_paper", "citing_author",
                                         "citing_paper_link", "cited_paper", "cited_paper_link"])
        plot_geoloc(map_data, Path(output_dir))
        citations_summary.save(Path(output_dir).joinpath("citation_summary.xlsx"))
