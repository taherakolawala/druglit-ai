import requests
import xmltodict
import pandas as pd
from typing import List, Dict
import time

class PubMedFetcher:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        
    def get_ids(self, query: str, retmax: int = 20, db: str = "pubmed") -> List[str]:
        """Get PubMed IDs for a search query - Fixed version of your code"""
        search_url = f"{self.base_url}esearch.fcgi"
        
        params = {
            "db": db,
            "term": query,
            "retmax": retmax,
            "retmode": "json"  # JSON is easier than XML
        }
        
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Handle the case where no results found
            if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                return data['esearchresult']['idlist']
            else:
                print("No results found")
                return []
                
        except Exception as e:
            print(f"Error fetching IDs: {e}")
            return []
    
    def get_paper_details(self, pmids: List[str]) -> List[Dict]:
        """NEW: Get full paper details (titles, abstracts, etc.) from PMIDs"""
        if not pmids:
            return []
            
        fetch_url = f"{self.base_url}efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml'  # XML needed for detailed info
        }
        
        try:
            response = requests.get(fetch_url, params=params)
            response.raise_for_status()
            
            # Parse XML
            data = xmltodict.parse(response.content)
            
            # Handle different response structures
            if 'PubmedArticleSet' not in data:
                return []
                
            articles = data['PubmedArticleSet'].get('PubmedArticle', [])
            
            # Handle single article case
            if not isinstance(articles, list):
                articles = [articles]
            
            papers = []
            for article in articles:
                try:
                    paper_info = self._extract_paper_info(article)
                    if paper_info:  # Only add if extraction successful
                        papers.append(paper_info)
                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue
                    
            return papers
            
        except Exception as e:
            print(f"Error fetching paper details: {e}")
            return []
    
    def _extract_paper_info(self, article: dict) -> Dict:
        """Helper: Extract key info from PubMed XML article"""
        try:
            medline = article['MedlineCitation']
            paper_article = medline['Article']
            
            # Get title
            title = paper_article.get('ArticleTitle', 'No title')
            if isinstance(title, dict):
                title = title.get('#text', str(title))
            
            # Get abstract (can be complex structure)
            abstract_parts = paper_article.get('Abstract', {}).get('AbstractText', '')
            abstract = self._parse_abstract(abstract_parts)
            
            # Get other details
            journal = paper_article.get('Journal', {}).get('Title', 'Unknown journal')
            pmid = medline.get('PMID', {})
            if isinstance(pmid, dict):
                pmid = pmid.get('#text', 'Unknown')
            
            # Get publication date
            pub_date = self._get_publication_date(paper_article)
            
            return {
                'pmid': str(pmid),
                'title': str(title),
                'abstract': str(abstract),
                'journal': str(journal),
                'pub_date': pub_date
            }
            
        except Exception as e:
            print(f"Error extracting paper info: {e}")
            return None
    
    def _parse_abstract(self, abstract_parts) -> str:
        """Helper: Parse abstract from various XML formats"""
        if not abstract_parts:
            return "No abstract available"
            
        if isinstance(abstract_parts, str):
            return abstract_parts
        elif isinstance(abstract_parts, dict):
            return abstract_parts.get('#text', str(abstract_parts))
        elif isinstance(abstract_parts, list):
            # Multiple abstract sections (Background, Methods, etc.)
            sections = []
            for part in abstract_parts:
                if isinstance(part, dict):
                    text = part.get('#text', str(part))
                    label = part.get('@Label', '')
                    if label:
                        sections.append(f"{label}: {text}")
                    else:
                        sections.append(text)
                else:
                    sections.append(str(part))
            return " ".join(sections)
        else:
            return str(abstract_parts)
    
    def _get_publication_date(self, paper_article: dict) -> str:
        """Helper: Extract publication date"""
        try:
            # Try different date formats
            journal_issue = paper_article.get('Journal', {}).get('JournalIssue', {})
            pub_date = journal_issue.get('PubDate', {})
            
            year = pub_date.get('Year', '')
            month = pub_date.get('Month', '')
            
            if year:
                return f"{year}" + (f"-{month}" if month else "")
            else:
                return "Unknown"
        except:
            return "Unknown"
    
    def search_drug_discovery_papers(self, drug_target: str = "EGFR inhibitor", max_results: int = 10) -> pd.DataFrame:
        """Main method: Search for drug discovery papers and return full details"""
        
        # Build focused query
        query = f'"{drug_target}" AND (drug discovery OR drug development OR pharmacology) AND (cancer OR oncology OR therapy)'
        
        print(f"Searching PubMed for: {query}")
        
        # Step 1: Get paper IDs
        pmids = self.get_ids(query, retmax=max_results)
        print(f"Found {len(pmids)} paper IDs")
        
        if not pmids:
            print("No papers found. Try a different search term.")
            return pd.DataFrame()
        
        # Step 2: Get full paper details
        print("Fetching paper details...")
        papers = self.get_paper_details(pmids)
        print(f"Successfully parsed {len(papers)} papers")
        
        # Step 3: Return as DataFrame
        if papers:
            df = pd.DataFrame(papers)
            # Filter out papers with very short abstracts (likely not research papers)
            df = df[df['abstract'].str.len() > 100]
            return df
        else:
            return pd.DataFrame()

# Test the enhanced fetcher
if __name__ == "__main__":
    fetcher = PubMedFetcher()
    
    # Test 1: Basic ID fetching (your original method)
    print("=== Testing ID Fetching ===")
    ids = fetcher.get_ids("EGFR inhibitor", retmax=3)
    print(f"Paper IDs: {ids}")
    
    # Test 2: Full paper details
    print("\n=== Testing Paper Details ===")
    if ids:
        papers = fetcher.get_paper_details(ids[:2])  # Just test 2 papers
        for paper in papers:
            print(f"\nTitle: {paper['title'][:100]}...")
            print(f"Journal: {paper['journal']}")
            print(f"Abstract: {paper['abstract'][:200]}...")
    
    # Test 3: Complete drug discovery search
    print("\n=== Testing Complete Search ===")
    df = fetcher.search_drug_discovery_papers("kinase inhibitor", max_results=3)
    if not df.empty:
        print(f"\nFound {len(df)} papers:")
        print(df[['title', 'journal', 'pub_date']].head())
    else:
        print("No papers found")