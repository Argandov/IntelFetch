# Intel Fetch (Beta)

A python program that fetches Threat Intelligence from a custom ("Programmable") Google search engine, filtered by keywords, compiles all the results and uses OpenAI OR Anthropic's Claude 3 to analyze this information.

1. User provides a set of keywords to be searched through Google by a specific custom search engine,
2. IntelFetch performs a Google search for this keywords using OR operands,
3. IntelFetch sends this search results to OpenAI with some context (Prompting) to curate this threat intelligence and provide some analysis.

This is the first iteration and the first beta test.
