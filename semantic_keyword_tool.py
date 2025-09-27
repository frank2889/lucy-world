#!/usr/bin/env python3
"""
Semantic Keyword Research Tool
Dit programma zoekt semantische zoekwoorden en vragen gerelateerd aan een hoofdzoekwoord
en toont het zoekvolume voor elk resultaat.
"""

import requests
import json
import time
from typing import List, Dict, Tuple
from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Laad omgevingsvariabelen
load_dotenv()

@dataclass
class KeywordData:
    """Data class voor zoekwoord informatie"""
    keyword: str
    search_volume: int
    difficulty: float = 0.0
    cpc: float = 0.0
    
class SemanticKeywordTool:
    """Hoofdklasse voor het semantic keyword research tool"""
    
    def __init__(self):
        # API configuratie (je kunt hier verschillende API providers gebruiken)
        self.serp_api_key = os.getenv('SERP_API_KEY')
        self.semrush_api_key = os.getenv('SEMRUSH_API_KEY')
        self.ahrefs_api_key = os.getenv('AHREFS_API_KEY')
        
    def get_related_questions(self, main_keyword: str) -> List[str]:
        """
        Haalt gerelateerde vragen op via Google's "People Also Ask" sectie
        """
        related_questions = []
        
        # Simulatie van People Also Ask vragen (in productie zou je een echte API gebruiken)
        question_patterns = [
            f"wat is {main_keyword}",
            f"hoe {main_keyword}",
            f"waar kan ik {main_keyword}",
            f"wanneer {main_keyword}",
            f"waarom {main_keyword}",
            f"welke {main_keyword}",
            f"hoeveel kost {main_keyword}",
            f"beste {main_keyword}",
            f"{main_keyword} tips",
            f"{main_keyword} kosten",
            f"{main_keyword} online",
            f"{main_keyword} in de buurt",
            f"{main_keyword} vergelijken",
            f"{main_keyword} reviews",
            f"{main_keyword} ervaringen"
        ]
        
        return question_patterns
    
    def get_semantic_keywords(self, main_keyword: str) -> List[str]:
        """
        Haalt semantisch gerelateerde zoekwoorden op
        """
        semantic_keywords = []
        
        # Voor "taart bestellen" voorbeeld
        if "taart" in main_keyword.lower():
            semantic_base = [
                "taart bezorgen", "taart kopen", "gebak bestellen", "verjaardagstaart",
                "bruidstaart", "taart maken", "bakkerij", "patisserie", "cake bestellen",
                "zoete lekkernijen", "dessert bestellen", "feesttaart", "kindertaart",
                "chocoladetaart", "fruittaart", "slagroomtaart", "fondant taart"
            ]
        else:
            # Algemene semantische patronen
            semantic_base = [
                f"{main_keyword} online",
                f"{main_keyword} kopen",
                f"{main_keyword} bestellen",
                f"{main_keyword} service",
                f"{main_keyword} bedrijf",
                f"goedkope {main_keyword}",
                f"beste {main_keyword}",
                f"professionele {main_keyword}",
                f"{main_keyword} Amsterdam",
                f"{main_keyword} Rotterdam",
                f"{main_keyword} Utrecht"
            ]
        
        return semantic_base
    
    def get_search_volume_mock(self, keyword: str) -> KeywordData:
        """
        Mock functie voor zoekvolume data (in productie zou je een echte API gebruiken)
        """
        # Simuleer realistische zoekvolumes gebaseerd op keyword lengte en populariteit
        import hashlib
        import random
        
        # Gebruik hash voor consistente "random" waarden
        hash_object = hashlib.md5(keyword.encode())
        seed = int(hash_object.hexdigest()[:8], 16)
        random.seed(seed)
        
        # Basis zoekvolume afhankelijk van keyword type
        base_volume = 1000
        if any(word in keyword.lower() for word in ['bestellen', 'kopen', 'online']):
            base_volume = 2000
        if any(word in keyword.lower() for word in ['goedkope', 'beste', 'tips']):
            base_volume = 1500
        
        # Voeg variatie toe
        volume = random.randint(base_volume // 4, base_volume * 2)
        difficulty = random.uniform(20, 80)
        cpc = random.uniform(0.5, 3.0)
        
        return KeywordData(
            keyword=keyword,
            search_volume=volume,
            difficulty=round(difficulty, 1),
            cpc=round(cpc, 2)
        )
    
    def research_keywords(self, main_keyword: str) -> Dict[str, List[KeywordData]]:
        """
        Hoofdfunctie die alle keyword research uitvoert
        """
        print(f"🔍 Onderzoek wordt uitgevoerd voor: '{main_keyword}'")
        print("=" * 60)
        
        results = {
            'questions': [],
            'semantic_keywords': []
        }
        
        # Haal gerelateerde vragen op
        print("📋 Zoeken naar gerelateerde vragen...")
        questions = self.get_related_questions(main_keyword)
        for question in questions:
            keyword_data = self.get_search_volume_mock(question)
            results['questions'].append(keyword_data)
            time.sleep(0.1)  # Simuleer API rate limiting
        
        # Haal semantische zoekwoorden op
        print("🔗 Zoeken naar semantische zoekwoorden...")
        semantic_keywords = self.get_semantic_keywords(main_keyword)
        for keyword in semantic_keywords:
            keyword_data = self.get_search_volume_mock(keyword)
            results['semantic_keywords'].append(keyword_data)
            time.sleep(0.1)  # Simuleer API rate limiting
        
        return results
    
    def display_results(self, results: Dict[str, List[KeywordData]]) -> None:
        """
        Toont de resultaten in een overzichtelijke format
        """
        print("\n" + "=" * 80)
        print("📊 RESULTATEN KEYWORD ONDERZOEK")
        print("=" * 80)
        
        # Toon gerelateerde vragen
        print("\n🙋‍♀️ GERELATEERDE VRAGEN:")
        print("-" * 40)
        questions = sorted(results['questions'], key=lambda x: x.search_volume, reverse=True)
        for i, question_data in enumerate(questions, 1):
            print(f"{i:2d}. {question_data.keyword}")
            print(f"    📈 Zoekvolume: {question_data.search_volume:,}")
            print(f"    💰 CPC: €{question_data.cpc}")
            print(f"    📊 Difficulty: {question_data.difficulty}/100")
            print()
        
        # Toon semantische zoekwoorden
        print("\n🔗 SEMANTISCHE ZOEKWOORDEN:")
        print("-" * 40)
        keywords = sorted(results['semantic_keywords'], key=lambda x: x.search_volume, reverse=True)
        for i, keyword_data in enumerate(keywords, 1):
            print(f"{i:2d}. {keyword_data.keyword}")
            print(f"    📈 Zoekvolume: {keyword_data.search_volume:,}")
            print(f"    💰 CPC: €{keyword_data.cpc}")
            print(f"    📊 Difficulty: {keyword_data.difficulty}/100")
            print()
        
        # Samenvatting
        total_volume = sum(k.search_volume for k in questions + keywords)
        print(f"\n📈 SAMENVATTING:")
        print(f"Totaal aantal keywords: {len(questions) + len(keywords)}")
        print(f"Totaal zoekvolume: {total_volume:,}")
        print(f"Gemiddeld zoekvolume: {total_volume // (len(questions) + len(keywords)):,}")
    
    def export_to_csv(self, results: Dict[str, List[KeywordData]], filename: str = "keyword_research.csv") -> None:
        """
        Exporteert resultaten naar CSV bestand
        """
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['type', 'keyword', 'search_volume', 'difficulty', 'cpc']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            # Schrijf vragen
            for question_data in results['questions']:
                writer.writerow({
                    'type': 'question',
                    'keyword': question_data.keyword,
                    'search_volume': question_data.search_volume,
                    'difficulty': question_data.difficulty,
                    'cpc': question_data.cpc
                })
            
            # Schrijf semantische zoekwoorden
            for keyword_data in results['semantic_keywords']:
                writer.writerow({
                    'type': 'semantic',
                    'keyword': keyword_data.keyword,
                    'search_volume': keyword_data.search_volume,
                    'difficulty': keyword_data.difficulty,
                    'cpc': keyword_data.cpc
                })
        
        print(f"✅ Resultaten geëxporteerd naar: {filename}")

def main():
    """Hoofdfunctie van het programma"""
    print("🎯 SEMANTIC KEYWORD RESEARCH TOOL")
    print("=" * 50)
    
    # Initialiseer de tool
    tool = SemanticKeywordTool()
    
    # Vraag gebruiker om input
    main_keyword = input("Voer uw hoofdzoekwoord in: ").strip()
    
    if not main_keyword:
        print("❌ Geen zoekwoord ingevoerd!")
        return
    
    # Voer keyword onderzoek uit
    try:
        results = tool.research_keywords(main_keyword)
        tool.display_results(results)
        
        # Vraag of gebruiker wil exporteren
        export = input("\nWilt u de resultaten exporteren naar CSV? (j/n): ").strip().lower()
        if export in ['j', 'ja', 'y', 'yes']:
            filename = f"keyword_research_{main_keyword.replace(' ', '_')}.csv"
            tool.export_to_csv(results, filename)
        
    except Exception as e:
        print(f"❌ Er is een fout opgetreden: {e}")

if __name__ == "__main__":
    main()