from cti_modules.openai_first_analysis import call_openai
from cti_data.system import system_context

import sys
import requests
import json
from dateutil import parser
from dotenv import dotenv_values, load_dotenv

model = "gpt-4"
date_restrict = "m3"
load_dotenv()
GOOGLE_API_KEY = s.environ.get("GOOGLE_API_KEY")
OPENAI_API_KEY = s.environ.get("OPENAI_API_KEY")
SEARCH_ENGINE_ID = s.environ.get("SEARCH_ENGINE_ID")

def search_google(Q, GOOGLE_API_KEY, SEARCH_ENGINE_ID, date_restrict):
    search_pages = []
    pages = [1,2,3,4]
    for page in pages:
        start = (page - 1) * 10 + 1
        url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={Q}&start={start}&dateRestrict={date_restrict}"
        data = requests.get(url).json()
        search_page = data.get("items")
        search_pages.append(search_page)
    return search_pages

def define_search_queries():
    keywords = []
    with open('cti_input_data/keywords.txt', 'r') as file:
     for line in file:
         keywords.append(line.strip())
    # Google query to be added to the REST request URL:
    Q = '+OR+'.join(keywords)
    google_query = Q.replace(' ', '+')

    return google_query, KEYWORD_LIST

def extract_data(search_pages, index, COUNTER):
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
        except ValueError:
            result_published_date = "N/A"
    
        # get the page title
        RESULT_TITLE = search_item.get("title")
        # page snippet
        RESULT_SNIPPET = search_item.get("snippet")
        # alternatively, you can get the HTML snippet (bolded keywords)
        html_snippet = search_item.get("htmlSnippet")
        # extract the page url
        result_link = search_item.get("link")
        
        buffer = "="*10
        data_separator = buffer + f"Result #{i+COUNTER}" + buffer
        PAGE_SEARCH_RESULTS += data_separator + "\n"
        PAGE_SEARCH_RESULTS += "Title: " + RESULT_TITLE + "\n"
            # Article description:
        PAGE_SEARCH_RESULTS += "Description: " + RESULT_SNIPPET + "\n"
        PAGE_SEARCH_RESULTS += "Date: " + result_published_date + "\n"
        PAGE_SEARCH_RESULTS += "Long Description: " + RESULT_LONG_DESCRIPTION + "\n"
        PAGE_SEARCH_RESULTS += "URL: " + result_link + "\n"
    return PAGE_SEARCH_RESULTS
    
print(PAGE_SEARCH_RESULTS)

#print(response)
#print("______________")
#print(tokens_used)

sys.exit(1)
google_query, KEYWORD_LIST = define_search_queries()
search_pages = search_google(google_query, GOOGLE_API_KEY, SEARCH_ENGINE_ID, date_restrict)
COUNTER = 0
output_pages = []
for i in range(0, len(search_pages)):
    # Index will be from 1 to the amount of pages we look for in Google
    index = i+1
    output_pages.append(extract_data(search_pages[i], index, COUNTER))
    COUNTER += 1

    # THIS IS FOR DEBUGGING AND PRINTING TO STDOUT ONLY:
for page in output_pages:
    print(page)

total_data_string = ""
for page in output_pages:
    total_data_string + page + "\n"

response, tokens_used = call_openai(\
                                    OPENAI_API_KEY, \
                                    KEYWORD_LIST, \
                                    system_context, \
                                    PAGE_SEARCH_RESULTS, \
                                    model)

print(f"Number of pages scraped: {len(output_pages)}")
