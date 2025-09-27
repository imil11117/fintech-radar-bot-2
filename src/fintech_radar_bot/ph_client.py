"""
Product Hunt GraphQL client for fetching product information.
"""

import os
import requests
from typing import Dict, List, Optional
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
            Dict containing normalized post data or None if not found
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
                topics(first: 10) {
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
                    name
                    username
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
            if post:
                return self._normalize_post_data(post)
            return None
            
        except (ValueError, ConnectionError) as e:
            print(f"Error fetching post by slug '{slug}': {str(e)}")
            return None
    
    def get_recent_posts(self, posted_after_iso: str, limit: int = 30) -> List[Dict]:
        """
        Get recent posts from Product Hunt posted after a specific date.
        
        Args:
            posted_after_iso: ISO date string (e.g., "2024-01-01T00:00:00Z")
            limit: Maximum number of posts to fetch (default: 30)
            
        Returns:
            List of normalized post dictionaries
        """
        query = """
        query ($after: DateTime!, $limit: Int!) {
            posts(postedAfter: $after, first: $limit) {
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
                        topics(first: 10) { edges { node { name slug } } }
                        thumbnail { url }
                        media { url type videoUrl }
                        makers { name username }
                        productLinks { type url }
                    }
                }
            }
        }
        """
        
        try:
            data = self._make_request(query, {
                "after": posted_after_iso,
                "limit": limit
            })
            
            posts_data = data.get("data", {}).get("posts", {}).get("edges", [])
            
            # Normalize each post
            normalized_posts = []
            for edge in posts_data:
                if edge.get("node"):
                    normalized_post = self._normalize_post_data(edge["node"])
                    normalized_posts.append(normalized_post)
            
            return normalized_posts
            
        except (ValueError, ConnectionError) as e:
            print(f"Error fetching recent posts: {str(e)}")
            return []

    def search_post_tophit(self, query: str) -> Optional[Dict]:
        """
        Search for a product and return the top hit.
        Note: Product Hunt API doesn't support direct search via GraphQL.
        This method attempts to find a post by treating the query as a slug.
        
        Args:
            query: Search query string (treated as slug)
            
        Returns:
            Dict containing normalized top post data or None if not found
        """
        # Since Product Hunt GraphQL API doesn't support search queries,
        # we'll try to find the post by treating the query as a slug
        # This is a fallback approach
        try:
            # Try to get the post by slug (treating query as slug)
            return self.get_post_by_slug(query)
            
        except (ValueError, ConnectionError) as e:
            print(f"Error searching for '{query}': {str(e)}")
            return None
    
    def _normalize_post_data(self, post: Dict) -> Dict:
        """
        Normalize post data to a flat structure.
        
        Args:
            post: Raw post data from GraphQL response
            
        Returns:
            Dict with normalized flat structure
        """
        # Extract topics (connection with edges)
        topics = []
        if post.get("topics", {}).get("edges"):
            topics = [
                edge["node"]["name"] 
                for edge in post["topics"]["edges"] 
                if edge.get("node")
            ]
        
        # Extract makers (plain list)
        makers = []
        if post.get("makers"):
            makers = [
                maker.get("name") 
                for maker in post["makers"] 
                if maker and maker.get("name")
            ]
        
        # Extract product links (plain list)
        product_links = post.get("productLinks", []) or []
        
        # Extract thumbnail URL
        thumbnail_url = None
        if post.get("thumbnail", {}).get("url"):
            thumbnail_url = post["thumbnail"]["url"]
        
        # Extract media (plain list)
        media = post.get("media", []) or []
        
        # Return normalized flat structure
        return {
            "id": post.get("id"),
            "name": post.get("name"),
            "tagline": post.get("tagline"),
            "description": post.get("description"),
            "votesCount": post.get("votesCount"),
            "commentsCount": post.get("commentsCount"),
            "slug": post.get("slug"),
            "website": post.get("website"),
            "url": post.get("url"),
            "createdAt": post.get("createdAt"),
            "topics": topics,
            "makers": makers,
            "thumbnailUrl": thumbnail_url,
            "media": media,
            "productLinks": product_links
        }


def create_ph_client() -> ProductHuntClient:
    """Factory function to create a ProductHuntClient instance."""
    return ProductHuntClient()
