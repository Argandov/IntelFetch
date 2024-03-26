import anthropic
from dotenv import dotenv_values
import json
import sys

def call_tier1(ANTHROPIC_API_KEY, keywords, system, search_results, model):
    client = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY,
            )

    merged_message = "CTI_0 data: \n"
    merged_message += search_results
    merged_message += "INFO: The following is a tech stack keyword list, for our relevant tech stack:\n"
    merged_message += keywords
    merged_message += "\n"

    response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    temperature=0,
    system=system,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": merged_message
                }
            ]
        }
    ]
)

    content = response.content[0].text
    total_tokens = int(response.usage.input_tokens) + int(response.usage.output_tokens)

    return content, total_tokens

    
def call_tier2(ANTHROPIC_API_KEY, system, JSON_CTI1, model):
    client = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY,
            )
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0,
        system=system,
        messages=[ {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": JSON_CTI1
                    } ] } ]
                )

    content = response.content[0].text
    total_tokens = int(response.usage.input_tokens) + int(response.usage.output_tokens)

    return content, total_tokens
