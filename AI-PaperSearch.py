import query_builder
import pubmeddownlload
# This file can be used to integrate the query builder and PubMed fetcher functionalities.

def user_request(natural_language_query: str, paper_count: int = 5):

    pubmed_query = query_builder.build_pubmed_query(natural_language_query)
    print(f"Generated PubMed Query: {pubmed_query}")

    pubmeddownlload.fetch_pubmed_papers(
        query=pubmed_query,
        email="taher.yakolawala@gmail.com",
        max_results=paper_count,
    )
    print("Papers fetched and saved successfully.")

if __name__ == "__main__":
    user_request("Find papers from the past year on nano-particle drug delivery for cancer treatment")

