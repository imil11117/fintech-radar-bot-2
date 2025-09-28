"""
Tests for finance subcategories functionality.
"""

import pytest
from src.fintech_radar_bot.finance_subcats import topic_hits_finance_subcat, FINANCE_SUBCATS
from src.fintech_radar_bot.discovery import filter_finance_subcats, pick_random, pick_round_robin


class TestFinanceSubcats:
    """Test finance subcategories matching and filtering."""
    
    def test_topic_hits_finance_subcat_exact_match(self):
        """Test exact case-insensitive matching."""
        topics = ["Investing", "Web Development"]
        hit, matched = topic_hits_finance_subcat(topics)
        assert hit is True
        assert "Investing" in matched
    
    def test_topic_hits_finance_subcat_case_insensitive(self):
        """Test case-insensitive matching."""
        topics = ["investing", "web development"]
        hit, matched = topic_hits_finance_subcat(topics)
        assert hit is True
        assert "Investing" in matched
    
    def test_topic_hits_finance_subcat_no_match(self):
        """Test when no finance subcategories match."""
        topics = ["Web Development", "Mobile Apps", "Design Tools"]
        hit, matched = topic_hits_finance_subcat(topics)
        assert hit is False
        assert matched == []
    
    def test_topic_hits_finance_subcat_empty_list(self):
        """Test with empty topics list."""
        topics = []
        hit, matched = topic_hits_finance_subcat(topics)
        assert hit is False
        assert matched == []
    
    def test_topic_hits_finance_subcat_none(self):
        """Test with None topics."""
        hit, matched = topic_hits_finance_subcat(None)
        assert hit is False
        assert matched == []
    
    def test_topic_hits_finance_subcat_multiple_matches(self):
        """Test multiple subcategory matches."""
        topics = ["Investing", "Payroll software", "Web Development"]
        hit, matched = topic_hits_finance_subcat(topics)
        assert hit is True
        assert len(matched) == 2
        assert "Investing" in matched
        assert "Payroll software" in matched


class TestFilterFinanceSubcats:
    """Test filtering posts by finance subcategories."""
    
    def test_filter_finance_subcats_matches(self):
        """Test filtering posts that match finance subcategories."""
        posts = [
            {
                "id": "1",
                "name": "Investment App",
                "topics": ["Investing", "Mobile Apps"]
            },
            {
                "id": "2", 
                "name": "Web Dev Tool",
                "topics": ["Web Development", "Design"]
            },
            {
                "id": "3",
                "name": "Payroll System",
                "topics": ["Payroll software", "HR"]
            }
        ]
        
        filtered = filter_finance_subcats(posts)
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "3"
        assert "_matched_subcats" in filtered[0]
        assert "_matched_subcats" in filtered[1]
    
    def test_filter_finance_subcats_no_matches(self):
        """Test filtering when no posts match finance subcategories."""
        posts = [
            {
                "id": "1",
                "name": "Web Dev Tool",
                "topics": ["Web Development", "Design"]
            },
            {
                "id": "2",
                "name": "Mobile Game",
                "topics": ["Games", "Entertainment"]
            }
        ]
        
        filtered = filter_finance_subcats(posts)
        assert len(filtered) == 0
    
    def test_filter_finance_subcats_empty_posts(self):
        """Test filtering with empty posts list."""
        posts = []
        filtered = filter_finance_subcats(posts)
        assert len(filtered) == 0


class TestSelectionStrategies:
    """Test selection strategies for finance subcategory posts."""
    
    def test_pick_random_with_posts(self):
        """Test random selection with available posts."""
        posts = [
            {"id": "1", "name": "App 1"},
            {"id": "2", "name": "App 2"},
            {"id": "3", "name": "App 3"}
        ]
        
        # Test multiple times to ensure randomness
        selected_ids = set()
        for _ in range(10):
            pick = pick_random(posts)
            assert pick is not None
            selected_ids.add(pick["id"])
        
        # Should have selected different posts (very likely with 3 posts and 10 attempts)
        assert len(selected_ids) > 1
    
    def test_pick_random_empty_list(self):
        """Test random selection with empty list."""
        posts = []
        pick = pick_random(posts)
        assert pick is None
    
    def test_pick_round_robin_basic(self, tmp_path):
        """Test round-robin selection with state file."""
        import os
        
        posts = [
            {"id": "1", "name": "App 1", "_matched_subcats": ["Investing"]},
            {"id": "2", "name": "App 2", "_matched_subcats": ["Payroll software"]},
            {"id": "3", "name": "App 3", "_matched_subcats": ["Investing"]}
        ]
        
        state_path = tmp_path / "last_subcat.txt"
        
        # First selection should pick from first subcategory
        pick = pick_round_robin(posts, FINANCE_SUBCATS, str(state_path))
        assert pick is not None
        assert pick["id"] == "1"  # First Investing post
        
        # Second selection should pick from next subcategory
        pick = pick_round_robin(posts, FINANCE_SUBCATS, str(state_path))
        assert pick is not None
        assert pick["id"] == "2"  # Payroll software post
    
    def test_pick_round_robin_no_matches(self, tmp_path):
        """Test round-robin selection when no posts match any subcategory."""
        posts = [
            {"id": "1", "name": "App 1", "_matched_subcats": ["Non-finance"]}
        ]
        
        state_path = tmp_path / "last_subcat.txt"
        pick = pick_round_robin(posts, FINANCE_SUBCATS, str(state_path))
        assert pick is None
    
    def test_pick_round_robin_empty_list(self, tmp_path):
        """Test round-robin selection with empty posts list."""
        posts = []
        state_path = tmp_path / "last_subcat.txt"
        pick = pick_round_robin(posts, FINANCE_SUBCATS, str(state_path))
        assert pick is None
