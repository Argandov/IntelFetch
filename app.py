import sys
import os
import requests
from dateutil import parser
from dotenv import dotenv_values, load_dotenv
import random
import json
import urllib.parse

from cti_data.system import system_context, system_newsletter

    # VARIABLES
date_restrict = "m3" # m3 = past 3 months
total_pages = 1 # Total number of Google pages to query

    # LOAD ENV VARS
load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

# TEMPORARY: Check if argument is either "claude" or "gpt":
if sys.argv[1] == "claude3":
    model = "claude-3-opus-20240229"
    from cti_modules.tier1Claude import call_tier1, call_tier2
    LLM_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
elif sys.argv[1] == "gpt4":
    model = "gpt-4"
    from cti_modules.tier1OpenAI import call_tier1, call_tier2
    LLM_API_KEY = os.environ.get("OPENAI_API_KEY")
else:
    print("Invalid argument. Please use 'claude3' or 'gpt4'.")
    sys.exit(1)



def search_google(Q, GOOGLE_API_KEY, SEARCH_ENGINE_ID, date_restrict, total_pages):
    """Function to execute Google search."""
    search_pages = []
        # Iterate over defined No. of pages to scrape, and then append the search results for every page
    total_pages = total_pages + 1
    for page in range(1, total_pages):
        start = (page - 1) * 10 + 1
        url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={Q}&start={start}&dateRestrict={date_restrict}"
        # PRINT A REDACTED (FOR DEBUGGING PURPOSES)
        url_redacted = f"https://www.googleapis.com/customsearch/v1?key=XXXXXXXXX&cx={SEARCH_ENGINE_ID}&q={Q}&start={start}&dateRestrict={date_restrict}"
        print(url_redacted)
        data = requests.get(url).json()
        search_page = data.get("items")
        search_pages.append(search_page)
    if search_pages == []:
        print("No results found")
        sys.exit(1)
    else:
        print(f"[+] Found {len(search_pages)} results")
    return search_pages


def define_search_queries():
    KEYWORD_LIST = []
    try:
        with open('cti_input_data/keywords.txt', 'r') as file:
            for line in file:
                KEYWORD_LIST.append(line.strip())

        # Construct Google query with OR conditions
        query_terms = ' OR '.join(['(' + term + ')' for term in KEYWORD_LIST])
        google_query = urllib.parse.quote(query_terms)

        return google_query, KEYWORD_LIST
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return None, None
    except Exception as e:
        print("An error occurred:", e)
        return None, None


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

        buffer = "=" * 25
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
search_pages = search_google(google_query, GOOGLE_API_KEY, SEARCH_ENGINE_ID, date_restrict, total_pages)
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
    #print(page)
    PAGE_SEARCH_RESULTS += page


    # Transform the keyword list into a str
KEYWORDS = '\n'.join(KEYWORD_LIST)

#input("[+] Enter to continue.")
print(PAGE_SEARCH_RESULTS)
# Press Enter to continue:
input("[+] Enter to continue.")

print(f"[+] Opening LLM {model} at TIER1...")
response, tokens_used = call_tier1(
        LLM_API_KEY,
        KEYWORDS,
        system_context,
        PAGE_SEARCH_RESULTS,
        model)
try:
    JSON_CTI1 = json.dumps(response)
    print(f"[i] TIER1 Finished. Tokens used in CTI_1: {tokens_used}")
except Exception as e:
    print(response)
    print(f"[!] ERROR: {e}")
    sys.exit(1)

if JSON_CTI1:
    print(f"[+] Opening LLM {model} at TIER1...")
    response, tokens_used = call_tier2(
            LLM_API_KEY,
            system_newsletter,
            JSON_CTI1,
            model)
    print(f"[i] TIER2 Finished. Tokens used in CTI_2: {tokens_used}")
    # Create a new .md file in the output/ folder with a random name, and put "response" contents into it:
    outfile = f"{random.randint(100,20000)}.md"
    with open(f'output/{outfile}', 'w') as file:
        outfile_contents = response + "\n" + "---" + "\n" + PAGE_SEARCH_RESULTS
        file.write(outfile_contents)
        print(f"[i] File written at \noutput/{outfile}")

print("SUCCESS: TIER1 and TIER2 completed. Exiting...")
