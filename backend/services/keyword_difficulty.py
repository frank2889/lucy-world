#!/usr/bin/env python3
"""
Keyword Difficulty Analysis Service
Analyzes SERP competition to provide difficulty scores
"""
import requests
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from urllib.parse import quote_plus
import time

@dataclass
class SERPResult:
    url: str
    title: str
    domain: str
    is_big_brand: bool
    has_exact_match: bool

@dataclass
class KeywordDifficulty:
    keyword: str
    difficulty_score: int  # 0-100 (0=easy, 100=very hard)
    reasoning: str
    serp_features: List[str]
    top_domains: List[str]
    competition_level: str  # "Low", "Medium", "High", "Very High"

class KeywordDifficultyAnalyzer:
    def __init__(self):
        self.big_brands = {
            'wikipedia.org', 'amazon.com', 'youtube.com', 'facebook.com',
            'linkedin.com', 'twitter.com', 'instagram.com', 'pinterest.com',
            'reddit.com', 'quora.com', 'medium.com', 'hubspot.com',
            'salesforce.com', 'microsoft.com', 'google.com', 'apple.com',
            'forbes.com', 'cnn.com', 'bbc.com', 'nytimes.com'
        }
        
    def analyze_keyword_difficulty(self, keyword: str, language: str = 'en', country: str = 'US') -> KeywordDifficulty:
        """
        Analyze keyword difficulty by examining SERP results
        """
        try:
            # Simulate SERP analysis (in production, would use real SERP API)
            serp_data = self._fetch_serp_data(keyword, language, country)
            
            difficulty_score = self._calculate_difficulty_score(serp_data, keyword)
            reasoning = self._generate_reasoning(serp_data, difficulty_score)
            competition_level = self._get_competition_level(difficulty_score)
            
            return KeywordDifficulty(
                keyword=keyword,
                difficulty_score=difficulty_score,
                reasoning=reasoning,
                serp_features=serp_data.get('features', []),
                top_domains=[r['domain'] for r in serp_data.get('results', [])[:5]],
                competition_level=competition_level
            )
            
        except Exception as e:
            # Fallback difficulty estimation
            return self._estimate_difficulty_fallback(keyword)
    
    def _fetch_serp_data(self, keyword: str, language: str, country: str) -> Dict:
        """
        Fetch SERP data (mock implementation - would use real SERP API in production)
        """
        # Mock SERP data based on keyword characteristics
        word_count = len(keyword.split())
        char_length = len(keyword)
        
        # Simulate different difficulty scenarios
        if any(brand in keyword.lower() for brand in ['amazon', 'google', 'apple', 'microsoft']):
            # Brand keywords = very competitive
            results = [
                {'domain': 'amazon.com', 'title': f'{keyword} - Amazon Official', 'url': 'https://amazon.com'},
                {'domain': 'wikipedia.org', 'title': f'{keyword} - Wikipedia', 'url': 'https://wikipedia.org'},
                {'domain': 'forbes.com', 'title': f'Best {keyword} 2025', 'url': 'https://forbes.com'},
            ]
            features = ['featured_snippet', 'knowledge_panel', 'shopping_ads']
        elif word_count >= 4:
            # Long-tail = less competitive
            results = [
                {'domain': 'smallblog.com', 'title': f'How to {keyword}', 'url': 'https://smallblog.com'},
                {'domain': 'guide-site.org', 'title': f'{keyword} Complete Guide', 'url': 'https://guide-site.org'},
                {'domain': 'forum-discussion.net', 'title': f'{keyword} Discussion', 'url': 'https://forum-discussion.net'},
            ]
            features = ['people_also_ask']
        else:
            # Medium competition
            results = [
                {'domain': 'industry-leader.com', 'title': f'{keyword} Solutions', 'url': 'https://industry-leader.com'},
                {'domain': 'expert-blog.net', 'title': f'Best {keyword} Guide', 'url': 'https://expert-blog.net'},
                {'domain': 'review-site.org', 'title': f'{keyword} Reviews 2025', 'url': 'https://review-site.org'},
            ]
            features = ['featured_snippet', 'people_also_ask']
        
        return {
            'results': results,
            'features': features,
            'total_results': max(1000000 - (word_count * 100000), 50000)
        }
    
    def _calculate_difficulty_score(self, serp_data: Dict, keyword: str) -> int:
        """
        Calculate difficulty score based on SERP analysis
        """
        score = 0
        results = serp_data.get('results', [])
        
        # Factor 1: Big brand presence (40% weight)
        big_brand_count = sum(1 for r in results[:10] if any(brand in r['domain'] for brand in self.big_brands))
        score += min(big_brand_count * 8, 40)
        
        # Factor 2: SERP features (30% weight)
        features = serp_data.get('features', [])
        if 'knowledge_panel' in features:
            score += 15
        if 'featured_snippet' in features:
            score += 10
        if 'shopping_ads' in features:
            score += 5
        
        # Factor 3: Keyword characteristics (20% weight)
        word_count = len(keyword.split())
        if word_count == 1:
            score += 15  # Single words are competitive
        elif word_count == 2:
            score += 10
        elif word_count >= 4:
            score -= 5   # Long-tail easier
        
        # Factor 4: Commercial intent (10% weight)
        commercial_keywords = ['buy', 'price', 'cost', 'cheap', 'best', 'review', 'vs', 'comparison']
        if any(word in keyword.lower() for word in commercial_keywords):
            score += 10
        
        return min(max(score, 0), 100)
    
    def _generate_reasoning(self, serp_data: Dict, score: int) -> str:
        """
        Generate human-readable reasoning for the difficulty score
        """
        big_brands = sum(1 for r in serp_data.get('results', [])[:5] if any(brand in r['domain'] for brand in self.big_brands))
        features = serp_data.get('features', [])
        
        if score >= 80:
            return f"Very competitive - {big_brands} major brands in top 5, SERP features: {', '.join(features)}"
        elif score >= 60:
            return f"Highly competitive - {big_brands} established sites in top 5, moderate competition"
        elif score >= 40:
            return f"Medium competition - Mix of authority sites and smaller players"
        elif score >= 20:
            return f"Low competition - Mostly smaller sites, good opportunity for ranking"
        else:
            return f"Very low competition - Excellent opportunity for new content"
    
    def _get_competition_level(self, score: int) -> str:
        """Convert numeric score to competition level"""
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def _estimate_difficulty_fallback(self, keyword: str) -> KeywordDifficulty:
        """Fallback estimation when SERP data unavailable"""
        word_count = len(keyword.split())
        
        if word_count >= 4:
            score = 25  # Long-tail assumed easier
        elif word_count == 1:
            score = 70  # Single words competitive
        else:
            score = 45  # Medium
        
        return KeywordDifficulty(
            keyword=keyword,
            difficulty_score=score,
            reasoning="Estimated based on keyword length (SERP data unavailable)",
            serp_features=[],
            top_domains=[],
            competition_level=self._get_competition_level(score)
        )

# Example usage
if __name__ == "__main__":
    analyzer = KeywordDifficultyAnalyzer()
    
    test_keywords = [
        "pizza delivery",
        "best laptop 2025",
        "how to train a puppy at home",
        "amazon",
        "SEO"
    ]
    
    for keyword in test_keywords:
        difficulty = analyzer.analyze_keyword_difficulty(keyword)
        print(f"\n🎯 Keyword: {keyword}")
        print(f"📊 Difficulty: {difficulty.difficulty_score}/100 ({difficulty.competition_level})")
        print(f"💡 Reasoning: {difficulty.reasoning}")
        print(f"🌐 Top Domains: {', '.join(difficulty.top_domains[:3])}")