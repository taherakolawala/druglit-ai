from Bio import Entrez, Medline
import os
import requests
import csv
import json

class PubMedFetcher:
    def __init__(self, email, save_dir="papers"):
        """
        Initialize with your email (required by NCBI Entrez) and directory to save papers.
        """
        Entrez.email = email
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def search(self, query, max_results=5):
        """
        Search PubMed for the latest articles matching query.
        """
        handle = Entrez.esearch(db="pubmed", term=query, sort="date", retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        return record["IdList"]

    def fetch_metadata(self, id_list):
        """
        Fetch article metadata for a list of PubMed IDs.
        Returns list of dicts with metadata.
        """
        ids = ",".join(id_list)
        handle = Entrez.efetch(db="pubmed", id=ids, rettype="medline", retmode="text")
        records = Medline.parse(handle)
        metadata_list = []

        for record in records:
            metadata = {
                "PMID": record.get("PMID", ""),
                "Title": record.get("TI", ""),
                "Authors": record.get("AU", []),
                "Journal": record.get("JT", ""),
                "PublicationDate": record.get("DP", ""),
                "Abstract": record.get("AB", "")
            }
            metadata_list.append(metadata)

        handle.close()
        return metadata_list

    def save_metadata(self, metadata_list, filename="metadata"):
        """
        Save metadata to CSV and JSON.
        """
        csv_path = os.path.join(self.save_dir, f"{filename}.csv")
        json_path = os.path.join(self.save_dir, f"{filename}.json")

        # Save JSON
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(metadata_list, jf, indent=4)

        # Save CSV
        keys = ["PMID", "Title", "Authors", "Journal", "PublicationDate", "Abstract"]
        with open(csv_path, "w", newline="", encoding="utf-8") as cf:
            writer = csv.DictWriter(cf, fieldnames=keys)
            writer.writeheader()
            for entry in metadata_list:
                # Flatten authors list for CSV
                entry_copy = entry.copy()
                entry_copy["Authors"] = "; ".join(entry_copy["Authors"])
                writer.writerow(entry_copy)

        print(f"Metadata saved to:\n- {csv_path}\n- {json_path}")

    def download_pmc(self, pmid):
        """
        Try downloading full text from PubMed Central if available.
        """
        handle = Entrez.elink(dbfrom="pubmed", id=pmid, linkname="pubmed_pmc")
        record = Entrez.read(handle)
        handle.close()

        try:
            pmcid = record[0]['LinkSetDb'][0]['Link'][0]['Id']
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/pdf/"
            response = requests.get(url)
            if response.status_code == 200:
                filepath = os.path.join(self.save_dir, f"PMC{pmcid}.pdf")
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded: {filepath}")
            else:
                print(f"PDF not available for PMC{pmcid}")
        except (IndexError, KeyError):
            print(f"No PMC link for PMID {pmid}")


def sanitize_folder_name(name: str) -> str:
    """
    Sanitize a string to be used as a folder name by removing or replacing invalid characters.
    """
    # Replace various punctuation with underscores
    import re
    # Remove or replace characters that are invalid in Windows file names
    sanitized = re.sub(r'[<>:"/\\|?*\[\]\(\)]', '', name)
    # Replace multiple spaces or underscores with a single underscore
    sanitized = re.sub(r'[\s_]+', '_', sanitized)
    # Remove leading/trailing underscores and spaces
    sanitized = sanitized.strip('_').strip()
    # Ensure the name isn't empty
    if not sanitized:
        sanitized = "unnamed_query"
    return sanitized

def fetch_pubmed_papers(query: str, email: str, max_results: int = 5, save_dir: str = "papers") -> tuple[list[dict], str, str]:
    """
    A high-level function that combines all PubMed fetching functionality into one call.
    This function searches PubMed, fetches metadata, saves it to CSV and JSON, and attempts
    to download full-text PDFs if available.

    Args:
        query (str): The PubMed search query
        email (str): Your email address (required by NCBI)
        max_results (int, optional): Maximum number of results to fetch. Defaults to 100.
        save_dir (str, optional): Directory to save the results. Defaults to "papers".

    Returns:
        tuple[list[dict], str, str]: A tuple containing:
            - List of metadata dictionaries
            - Path to the CSV file
            - Path to the JSON file
    """
    # Create a query-specific directory inside save_dir with sanitized name
    query_dirname = sanitize_folder_name(query)
    query_dir = os.path.join(save_dir, query_dirname)
    os.makedirs(query_dir, exist_ok=True)
    
    # Initialize fetcher with the query-specific directory
    fetcher = PubMedFetcher(email=email, save_dir=query_dir)
    
    # Search for papers
    pmids = fetcher.search(query, max_results=max_results)
    print(f"Found {len(pmids)} papers matching the query")
    
    # Fetch and save metadata
    metadata_list = fetcher.fetch_metadata(pmids)
    fetcher.save_metadata(metadata_list, filename="metadata")
    
    # Try downloading full text PDFs
    print("\nAttempting to download full-text PDFs...")
    for pmid in pmids:
        fetcher.download_pmc(pmid)
        
    # Return the metadata and file paths
    csv_path = os.path.join(query_dir, "metadata.csv")
    json_path = os.path.join(query_dir, "metadata.json")
    
    return metadata_list, csv_path, json_path

# Example usage:
if __name__ == "__main__":
    # Use absolute path for papers directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    papers_dir = os.path.join(script_dir, "papers")
    
    query = "(agentic AI or AI agents) AND (drug discovery)"
    metadata, csv_file, json_file = fetch_pubmed_papers(
        query=query,
        email="taher.yakolawala@gmail.com",
        save_dir=papers_dir
    )
