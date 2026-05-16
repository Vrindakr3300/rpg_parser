import requests
from typing import List, Dict, Any

def fetch_spell_html(url: str) -> str:
    """Fetches the HTML content of an Archives of Nethys spell URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def fetch_spells_bulk(tradition: str = "primal", size: int = 1000) -> List[Dict[str, Any]]:
    """
    Fetches spells in bulk from the Archives of Nethys Elasticsearch API.
    By default fetches 'primal' spells.
    """
    url = "https://elasticsearch.aonprd.com/aon/_search?stats=search"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Elasticsearch DSL query to filter by type "spell" and the specified tradition
    payload = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"tradition": {"value": tradition.lower()}}},
                    {"term": {"type": {"value": "spell"}}}
                ]
            }
        },
        "size": size,
        "_source": True  # Fetch the full source data, including markdown and traits
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    hits = data.get("hits", {}).get("hits", [])
    
    # Extract the source documents from the hits
    return [hit.get("_source", {}) for hit in hits]

def fetch_spell_by_name(name: str) -> Dict[str, Any]:
    """
    Fetches a single spell by its exact name from the Archives of Nethys Elasticsearch API.
    """
    url = "https://elasticsearch.aonprd.com/aon/_search?stats=search"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"name.keyword": {"value": name}}},
                    {"term": {"type": {"value": "spell"}}}
                ]
            }
        },
        "size": 1,
        "_source": True
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    hits = data.get("hits", {}).get("hits", [])
    
    if not hits:
        raise ValueError(f"Spell not found: {name}")
        
    return hits[0].get("_source", {})
