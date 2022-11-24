import eutils
import pandas as pd
from pyaltmetric import Altmetric
import time
from time import mktime
import feedparser
from datetime import datetime
import argparse


def timeit(func):
    """
    Decorator for measuring function's running time.
    """

    def measure_time(*args, **kw):
        start_time = time.time()
        result = func(*args, **kw)
        print("Processing time of %s(): %.2f seconds."
              % (func.__qualname__, time.time() - start_time))
        return result

    return measure_time


@timeit
def pubmed(keyword, output, verbose=10, retmax=10):
    # Initializing API client
    client = eutils.Client(cache="cache_" + output, api_key="ff3ee99ef10393aeb7f137f4fd3815d53d08")
    print("Client initialized")

    # Retrieving PMIDs
    pmids = client.esearch(db="pubmed", term=keyword, retstart=0, retmax=retmax)
    print("PMID's retrieved")

    # Retrieving article information from all PMIDs
    articles = client.efetch(db="pubmed", id=pmids.ids)
    print("Article information retrieved")
    articles_iter = iter(articles)

    i = 0

    posts_overview = pd.DataFrame(columns=["Title", "PMID", "Published Year", "Journal", "Popularity"])
    while True:
        try:
            article = next(articles_iter)
            score = Altmetric()  # Instantiating Altmetric to fetch popularity score
            alt_info = score.pmid(str(article.pmid))

            posts_overview.loc[i] = [article.title,
                                     article.pmid,
                                     article.year,
                                     article.jrnl,
                                     int(round(alt_info["score"], 0)) if alt_info is not None else 0]  # Popularity score given by Altmetric. Defaults to 0 if score is not registered by Altmetric,
            i += 1
            if i % verbose == 0:
                print(f'{i} articles have been processed')

        except StopIteration:  # When iterator is empty, return dataframe as .csv-file
            return posts_overview.to_csv(str(output) + ".csv", sep=";")


#pubmed('"enhancer"[Title/Abstract] AND "chromatin"[MeSH Terms]', "1000test", 2445, 10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Positionals
    parser.add_argument("-k",
                        "--key",
                        type=str,
                        help="Keyterm(s) to be searched (use ' ' around your search)",
                        required=True,
                        metavar="")
    parser.add_argument("-o",
                        "--output",
                        type=str,
                        help="Output PREFIX",
                        required=True,
                        metavar="")

    # Conditionals
    parser.add_argument("-n",
                        "--number",
                        type=int,
                        choices=range(0,9999),
                        help="Max. number of articles to be returned (default is 10)",
                        default=10,
                        metavar="1-9999",
                        )
    parser.add_argument("-v",
                        "--verbose",
                        type=int,
                        choices=[1, 10, 100, 1000],
                        help="Updates you every time 1, 10, 100 or 1000 articles have been processed (default is 10)",
                        default=10)

    # Implementing arguments
    args = parser.parse_args()
    pubmed(args.key, args.output, args.verbose, args.number)
