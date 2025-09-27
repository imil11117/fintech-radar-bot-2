"""
Product Hunt GraphQL client for fetching product information.
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ProductHuntClient:
    """Client for interacting with Product Hunt GraphQL API."""
    
    def __init__(self):
        self.endpoint = "https://api.producthunt.com/v2/api/graphql"
        self.token = os.getenv("PRODUCTHUNT_TOKEN")
        
        if not self.token:
            raise ValueError("PRODUCTHUNT_TOKEN not found in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _make_request(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Make a GraphQL request to Product Hunt API."""
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise ValueError("Invalid PRODUCTHUNT_TOKEN. Please check your token.")
            elif response.status_code == 403:
                raise ValueError("Access forbidden. Please check your PRODUCTHUNT_TOKEN permissions.")
            
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                error_messages = [error.get("message", "Unknown error") for error in data["errors"]]
                raise ValueError(f"GraphQL errors: {'; '.join(error_messages)}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Product Hunt API: {str(e)}")
    
    def get_post_by_slug(self, slug: str) -> Optional[Dict]:
        """
        Get a product post by its slug.
        
        Args:
            slug: The product slug (e.g., "gusto")
            
        Returns:
            Dict containing post data or None if not found
        """
        query = """
        query GetPostBySlug($slug: String!) {
            post(slug: $slug) {
                id
                name
                tagline
                description
                votesCount
                commentsCount
                slug
                website
                url
                createdAt
                topics {
                    edges {
                        node {
                            name
                            slug
                        }
                    }
                }
                thumbnail {
                    url
                }
                media {
                    url
                    type
                    videoUrl
                }
                makers {
                    edges {
                        node {
                            name
                            username
                        }
                    }
                }
                productLinks {
                    type
                    url
                }
            }
        }
        """
        
        try:
            data = self._make_request(query, {"slug": slug})
            post = data.get("data", {}).get("post")
            return post if post else None
            
        except (ValueError, ConnectionError) as e:
            print(f"Error fetching post by slug '{slug}': {str(e)}")
            return None
    
    def search_post_tophit(self, query: str) -> Optional[Dict]:
        """
        Search for a product and return the top hit.
        
        Args:
            query: Search query string
            
        Returns:
            Dict containing the top post data or None if not found
        """
        search_query = """
        query SearchPosts($query: String!) {
            posts(query: $query, first: 1) {
                edges {
                    node {
                        id
                        name
                        tagline
                        description
                        votesCount
                        commentsCount
                        slug
                        website
                        url
                        createdAt
                        topics {
                            edges {
                                node {
                                    name
                                    slug
                                }
                            }
                        }
                        thumbnail {
                            url
                        }
                        media {
                            url
                            type
                            videoUrl
                        }
                        makers {
                            edges {
                                node {
                                    name
                                    username
                                }
                            }
                        }
                        productLinks {
                            type
                            url
                        }
                    }
                }
            }
        }
        """
        
        try:
            data = self._make_request(search_query, {"query": query})
            edges = data.get("data", {}).get("posts", {}).get("edges", [])
            
            if edges:
                return edges[0]["node"]
            return None
            
        except (ValueError, ConnectionError) as e:
            print(f"Error searching for '{query}': {str(e)}")
            return None


def create_ph_client() -> ProductHuntClient:
    """Factory function to create a ProductHuntClient instance."""
    return ProductHuntClient()
