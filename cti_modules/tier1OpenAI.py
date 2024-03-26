from openai import OpenAI
from dotenv import dotenv_values
import json
import sys

def call_tier1(OPENAI_API_KEY, keywords, system, search_results, model):
    client = OpenAI(api_key = OPENAI_API_KEY)

    merged_message = "CTI_0 data: \n"
    merged_message += search_results
    merged_message += "INFO: The following is a tech stack keyword list, for our relevant tech stack:\n"
    merged_message += keywords
    merged_message += "\n"

    messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": merged_message}
            ]
    
    openai_response = client.chat.completions.create(
        model = model,
        messages = messages
            )

    res = openai_response
    role = res.choices[0].message.role
    completion_tokens = res.usage.completion_tokens
    prompt_tokens = res.usage.prompt_tokens
    total_tokens_used = res.usage.total_tokens
    content = res.choices[0].message.content

    return content, prompt_tokens

    
def call_tier2(OPENAI_API_KEY, system, JSON_CTI1, model):
    client = OpenAI(api_key = OPENAI_API_KEY)

    messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": JSON_CTI1}
            ]
    
    openai_response = client.chat.completions.create(
        model = model,
        messages = messages
            )

    res = openai_response
    role = res.choices[0].message.role
    completion_tokens = res.usage.completion_tokens
    prompt_tokens = res.usage.prompt_tokens
    total_tokens_used = res.usage.total_tokens
    content = res.choices[0].message.content

    return content, prompt_tokens
