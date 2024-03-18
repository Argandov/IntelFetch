import sys
import os
import requests
from dateutil import parser
from dotenv import dotenv_values, load_dotenv

from cti_modules.openai_first_analysis import call_openai
from cti_data.system import system_context

# Variable declarations
model = "gpt-4"
date_restrict = "m3"

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")


def search_google(Q, GOOGLE_API_KEY, SEARCH_ENGINE_ID, date_restrict):
    """Function to execute Google search."""
    search_pages = []
    pages = [1, 2, 3, 4]
    for page in pages:
        start = (page - 1) * 10 + 1
        url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={Q}&start={start}&dateRestrict={date_restrict}"
        data = requests.get(url).json()
        search_page = data.get("items")
        search_pages.append(search_page)
    return search_pages


def define_search_queries():
    """Function to define the search queries."""
    KEYWORD_LIST = []
    with open('cti_input_data/keywords.txt', 'r') as file:
        for line in file:
            KEYWORD_LIST.append(line.strip())
    # Google query to be added to the REST request URL:
    Q = '+OR+'.join(KEYWORD_LIST)
    google_query = Q.replace(' ', '+')

    return google_query, KEYWORD_LIST


def extract_data(search_pages, index, COUNTER):
    """Function to extract data from the search pages."""
    PAGE_SEARCH_RESULTS = ""
    if COUNTER != 0:
        # If it's the first page (0), then do not add 10
        # "COUNTER" will become the incremental count of each result, in tens
        COUNTER = COUNTER * 10

    for i, search_item in enumerate(search_pages, start=1):
        try:
            RESULT_LONG_DESCRIPTION = search_item["pagemap"]["metatags"][0]["og:description"]
        except KeyError:
            RESULT_LONG_DESCRIPTION = "N/A"

        try:
            result_published_date = search_item["pagemap"]["metatags"][0].get("article:published_time", "N/A")
            date = parser.parse(result_published_date)
        except Exception:
            result_published_date = "N/A"

        # Get the page title
        RESULT_TITLE = search_item.get("title")
        # Page snippet
        RESULT_SNIPPET = search_item.get("snippet")
        # Alternatively, you can get the HTML snippet (bolded keywords)
        html_snippet = search_item.get("htmlSnippet")
        # Extract the page url
        result_link = search_item.get("link")

        buffer = "=" * 10
        data_separator = buffer + f"Result #{i+COUNTER}" + buffer
        PAGE_SEARCH_RESULTS += data_separator + "\n"
        PAGE_SEARCH_RESULTS += "Title: " + RESULT_TITLE + "\n"
        # Article description:
        PAGE_SEARCH_RESULTS += "Description: " + RESULT_SNIPPET + "\n"
        PAGE_SEARCH_RESULTS += "Date: " + result_published_date + "\n"
        PAGE_SEARCH_RESULTS += "Long Description: " + RESULT_LONG_DESCRIPTION + "\n"
        PAGE_SEARCH_RESULTS += "URL: " + result_link + "\n"

    return PAGE_SEARCH_RESULTS


# Main Function
google_query, KEYWORD_LIST = define_search_queries()
search_pages = search_google(google_query, GOOGLE_API_KEY, SEARCH_ENGINE_ID, date_restrict)
COUNTER = 0
output_pages = []

for i in range(len(search_pages)):
    # Index will be from 1 to the amount of pages we look for in Google
    index = i + 1
    output_pages.append(extract_data(search_pages[i], index, COUNTER))
    COUNTER += 1

    # Debugging and print statements
PAGE_SEARCH_RESULTS = ""
for page in output_pages:
    print(page)
    PAGE_SEARCH_RESULTS += page

print(type(PAGE_SEARCH_RESULTS))

    # Transform the keyword list into a str
KEYWORDS = '\n'.join(KEYWORD_LIST)

response, tokens_used = call_openai(
        OPENAI_API_KEY,
        KEYWORDS,
        system_context,
        PAGE_SEARCH_RESULTS,
        model)

print(response)
print(f"Number of pages scraped: {len(output_pages)}")
