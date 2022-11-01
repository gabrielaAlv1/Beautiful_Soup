import sys, argparse
from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError
from urllib.parse import urlparse

# version number
# and functions for dispatch table (replaced build_url function from previous versions)
VERSION = 3.04

# these globals will become class parameters once this is made into a class
site = ""
query = ""
depth = 0

def search_google(search_terms):
    """
    Searches google for a search term and returns the first link.

    :param search_terms: The term to search for
    :return: The fully built query string
    """
    # print(search_terms)
    search_terms = "+".join(search_terms.split())
    url = f'https://www.google.com/search?q={search_terms}'
    soup = BeautifulSoup(get_response(url), 'html.parser')

    # Uses class to find content, and prints as text
    for link in soup.findAll("a", href=True):
        if link.h3:
            follow = urlparse(link['href'][7:]).hostname
            if follow:
                return f"https://{follow}"
    return ""


def search_amazon(search_terms):
    """

    :param search_terms: The term to search for
    :return: The fully built query string
    """
    print(search_terms)
    search_terms = "+".join(search_terms.split())
    url = f'https://www.amazon.com/s?k={search_terms}'

    soup = BeautifulSoup(get_response(url), 'html.parser')
    # Uses class to find content, and prints as text
    for link in soup.find_all("p"):
        print(link.text)
        return f"https://{link.text}"


def search_wiki(search_terms):
    """

    :param search_terms: The term to search for
    :return: The fully built query string
    """
    print(search_terms)
    search_terms = "_".join(search_terms.split())
    url = f'https://en.wikipedia.org/wiki/{search_terms}_(disambiguation)'

    soup = BeautifulSoup(get_response(url), 'html.parser')
    # Uses class to find content, and prints as text
    for link in soup.find_all("li"):
        print(link.text)
        return link.text

def search_books(search_terms):
    """

    :param search_terms: The term to search for
    :return: The fully built query string
    """
    print(search_terms)
    search_terms = "+".join(search_terms.split())
    url = f'https://www.gutenberg.org/ebooks/search/?submit_search=Go%21&query={search_terms}'

    soup = BeautifulSoup(get_response(url), 'html.parser')
    # Uses class to find content, and prints as text
    my_List = []
    for link in soup.find_all('a', href=True):
        ebook_Link = link['href']
        my_List.append(f'https://www.gutenberg.org{ebook_Link}')
    return my_List, depth



sites = {
    "google": search_google,
    "amazon": search_amazon,
    "wikipedia": search_wiki,
    "wiki": search_wiki,
    "gutenberg": search_books,
    "books": search_books
}

def init() -> str:
    sysargs = argparse.ArgumentParser(description="Loads passed url to file after initial cleaning (munging)")
    sysargs.add_argument("-v", "--version", action="version", version=f"Current version is: {VERSION}")
    sysargs.add_argument("-s", "--site", help="The site to search (google, wikipedia, gutenberg, amazon)")
    sysargs.add_argument("-q", "--query", help="The term(s) to search for.")
    sysargs.add_argument("-d", "--depth", action="store", type=int, help=f"Stores up to 5 links:")
    args = sysargs.parse_args()

    global site
    global query
    global depth

    site = str(args.site).lower()

    try:
        if args.query:
            query = args.query
            depth = args.depth
            if args.depth > 0 and args.depth < 6:
                return sites.get(site)(query)
            else:
                print("Depth only goes until 5. Provide a valid depth")
                quit(1)
        else:
            print(
                "You must provide both the site (-s, --site) and query string (-q, --query) to use this program")
            quit(1)
    except (KeyError, TypeError) as ex:
        print("Acceptable sites to search for are: google, wikipedia(wiki), amazon, gutenberg(books)")
        quit(1)

def get_response(uri):
    # search, get and return a response from the url(s) provided

    if not uri.lower().startswith('http'):
        uri = f'https://{uri}'

    # Gets website URL and provides response (GET REQUEST)
    # If error - exits with exception
    try:
        response = requests.get(uri)
        response.raise_for_status()
    except HTTPError as httperr:
        print(f"HTTP error {httperr}")
        sys.exit(1)
    except Exception as err:
        print(f"Something went really wrong!: {err}")
        sys.exit(1)
    return response.text

if __name__ == '__main__':
    url, depth = init()
    count = 0
    depth = depth + 2
    for link in url:
        if depth >= count > 2:
            print(url[count])
            if get_response(link):
                query = "_".join(query.split())  # make text file as having a query with underscores instead of spaces
                with open(f"{site}_{query}.txt", "a", encoding="utf-8") as f:
                    f.write(get_response(link))  # TODO: have to loop over this and only print if you encounter search query
            else:
                print("First link was not followable or no links found")
        count = count + 1




