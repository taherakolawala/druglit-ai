import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import date

def build_pubmed_query(natural_language_query: str) -> str:
    """
    Convert a natural language query into a PubMed search query using OpenAI's GPT model.
    
    Args:
        natural_language_query (str): The natural language description of what to search for
        
    Returns:
        str: A formatted PubMed search query string
    """
    load_dotenv()
    client = OpenAI()

    today = date.today().strftime("%Y-%m-%d")

    response = client.chat.completions.create(
        model="gpt-4",  # Fixed typo in model name
        messages=[
            {
                "role": "system", 
                "content": f"You are an assistant that converts natural language requests into valid PubMed search queries. The current date is {today}. Return ONLY the query string."
            },
            {
                "role": "user", 
                "content": natural_language_query
            }
        ]
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    # Example usage
    query = "Find recent papers on AI for cancer diagnosis"
    result = build_pubmed_query(query)
    print(result)
