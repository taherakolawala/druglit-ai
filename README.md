# DrugLit-AI

AI-powered literature mining tool for drug discovery. This tool streamlines PubMed paper searches, downloads research papers, and organizes metadata for drug discovery research. Built with Python, it offers efficient paper management and data organization capabilities.

## Installation Guide

### Prerequisites
- Python 3.8 or higher
- Git
- OpenAI API key

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/taherakolawala/druglit-ai.git
   cd druglit-ai
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Windows
   python -m venv myenv
   myenv\Scripts\activate

   # Linux/MacOS
   python -m venv myenv
   source myenv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**
   - Create a `.env` file in the root directory
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

### Usage

1. **Search and Download Papers**
   ```bash
   python AI-PaperSearch.py
   ```
   This will:
   - Guide you through creating a PubMed search query
   - Display search results
   - Allow you to select and download papers
   - To make your queries, use the test command at the bottom of the file
   and change the query in the user_request() function there.

2. **Download Additional Papers**
   ```bash
   python pubmeddownlload.py
   ```
   Use this to download papers from existing queries or process new PubMed searches.

Downloaded papers and their metadata are automatically organized in the `papers/` directory, with separate folders for each search query.

### Project Structure
```
├── AI-PaperSearch.py      # Main search and download interface
├── pubmeddownlload.py     # Paper downloading functionality
├── query_builder.py       # Search query construction
└── papers/               # Downloaded papers and metadata
```

### Project Organization
Papers are organized in the `papers/` directory with the following structure:
```
papers/
└── search_query_name/
    ├── metadata.csv       # Paper details in CSV format
    └── metadata.json      # Paper details in JSON format
```

### Troubleshooting
- If you encounter any package installation issues, try updating pip:
  ```bash
  pip install --upgrade pip
  ```
- Make sure your OpenAI API key is correctly set in the `.env` file
- Check that you have sufficient permissions to write to the `papers/` directory

### Contributing
Contributions are welcome! Please feel free to submit a Pull Request.


