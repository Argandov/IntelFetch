from openai import OpenAI
from dotenv import dotenv_values
import sys

def call_openai(OPENAI_API_KEY, keyword_list, system, search_results, model):
    client = OpenAI(api_key = OPENAI_API_KEY)
    header_message = "The following is a tech stack keyword list, for our relevant tech stack:"

    merged_message = \
            search_results + "\n" + \
            header_message + "\n" + \
            keyword_list + "\n"

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
