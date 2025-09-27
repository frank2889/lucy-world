#!/usr/bin/env python3
"""
Quick Demo Script voor Semantic Keyword Research Tool
Dit script toont enkele voorbeelden van het gebruik van de tool
"""

from advanced_keyword_tool import AdvancedKeywordTool
import time

def demo_keywords():
    """Demonstratie met verschillende zoekwoorden"""
    
    print("🚀 SEMANTIC KEYWORD RESEARCH TOOL - DEMO")
    print("=" * 60)
    
    # Initialiseer tool
    tool = AdvancedKeywordTool()
    
    # Verschillende demo zoekwoorden
    demo_searches = [
        "webdesign",
        "koffie bestellen", 
        "auto verkopen",
        "cursus python"
    ]
    
    for i, keyword in enumerate(demo_searches, 1):
        print(f"\n📍 DEMO {i}/{len(demo_searches)}: '{keyword}'")
        print("-" * 40)
        
        try:
            # Haal keyword categorieën op
            keyword_categories = tool.get_comprehensive_keywords(keyword)
            
            # Toon beknopte resultaten
            print(f"✅ Gevonden categorieën:")
            for category, keywords in keyword_categories.items():
                print(f"  • {category.replace('_', ' ').title()}: {len(keywords)} keywords")
            
            # Toon top 3 van elke categorie
            print(f"\n🔍 Top resultaten:")
            for category, keywords in keyword_categories.items():
                if keywords:
                    print(f"\n  {category.replace('_', ' ').title()}:")
                    for j, kw in enumerate(keywords[:3], 1):
                        kd = tool.get_search_volume_advanced(kw)
                        volume_emoji = "🔥" if kd.search_volume > 1000 else "📈"
                        diff_emoji = "🟢" if kd.difficulty < 40 else "🟡" if kd.difficulty < 70 else "🔴"
                        print(f"    {j}. {kd.keyword}")
                        print(f"       {volume_emoji} Volume: {kd.search_volume:,} | {diff_emoji} Difficulty: {kd.difficulty}/100")
            
            print(f"\n" + "="*60)
            
            # Korte pauze tussen demo's
            if i < len(demo_searches):
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Fout bij '{keyword}': {e}")
    
    print(f"\n🎉 Demo voltooid!")
    print(f"💡 Gebruik 'python advanced_keyword_tool.py' voor interactief gebruik")
    print(f"🌐 Of start de web interface met 'python web_app.py'")

def quick_analysis(keyword):
    """Snelle analyse van een specifiek zoekwoord"""
    print(f"🔍 SNELLE ANALYSE: '{keyword}'")
    print("=" * 50)
    
    tool = AdvancedKeywordTool()
    
    # Haal data op
    keyword_categories = tool.get_comprehensive_keywords(keyword)
    
    # Verwerk alle keywords
    all_keywords_data = []
    for category, keywords in keyword_categories.items():
        for kw in keywords:
            kd = tool.get_search_volume_advanced(kw)
            all_keywords_data.append(kd)
    
    # Analyseer opportunities
    opportunities = tool.analyze_keyword_opportunities(all_keywords_data)
    
    # Toon samenvatting
    total_volume = sum(k.search_volume for k in all_keywords_data)
    
    print(f"📊 SAMENVATTING:")
    print(f"• Keywords gevonden: {len(all_keywords_data)}")
    print(f"• Totaal zoekvolume: {total_volume:,}")
    print(f"• Gemiddeld volume: {total_volume // len(all_keywords_data):,}")
    
    print(f"\n🎯 TOP OPPORTUNITEITEN:")
    
    # Toon beste opportunities
    if opportunities['low_competition']:
        print(f"\n🟢 Lage Competitie (makkelijk te ranken):")
        for i, kd in enumerate(opportunities['low_competition'][:3], 1):
            print(f"  {i}. {kd.keyword} (Volume: {kd.search_volume:,}, Difficulty: {kd.difficulty}/100)")
    
    if opportunities['high_volume_keywords']:
        print(f"\n🔥 Hoog Volume (veel zoekverkeer):")
        for i, kd in enumerate(opportunities['high_volume_keywords'][:3], 1):
            print(f"  {i}. {kd.keyword} (Volume: {kd.search_volume:,})")
    
    if opportunities['commercial_intent']:
        print(f"\n💰 Commerciële Intent (kopers):")
        for i, kd in enumerate(opportunities['commercial_intent'][:3], 1):
            print(f"  {i}. {kd.keyword} (Volume: {kd.search_volume:,})")

def main():
    """Hoofdfunctie voor demo script"""
    import sys
    
    if len(sys.argv) > 1:
        # Specifiek zoekwoord geanalyseerd
        keyword = ' '.join(sys.argv[1:])
        quick_analysis(keyword)
    else:
        # Run volledige demo
        demo_keywords()

if __name__ == "__main__":
    main()