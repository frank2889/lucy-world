#!/usr/bin/env python3
"""
Web Interface voor Semantic Keyword Research Tool
Een eenvoudige Flask webapplicatie voor het keyword research tool
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import csv
import io
from advanced_keyword_tool import AdvancedKeywordTool
import os
from datetime import datetime

app = Flask(__name__)

# Initialiseer de keyword tool
keyword_tool = AdvancedKeywordTool()

@app.route('/')
def index():
    """Hoofdpagina van de web interface"""
    return render_template('index.html')

@app.route('/api/research', methods=['POST'])
def research_keywords():
    """API endpoint voor keyword research"""
    try:
        data = request.json
        main_keyword = data.get('keyword', '').strip()
        
        if not main_keyword:
            return jsonify({'error': 'Geen zoekwoord opgegeven'}), 400
        
        # Voer keyword research uit
        keyword_categories = keyword_tool.get_comprehensive_keywords(main_keyword)
        
        # Verwerk alle keywords
        all_keywords_data = []
        processed_categories = {}
        
        for category, keywords in keyword_categories.items():
            category_data = []
            for keyword in keywords:
                keyword_data = keyword_tool.get_search_volume_advanced(keyword)
                category_data.append({
                    'keyword': keyword_data.keyword,
                    'search_volume': keyword_data.search_volume,
                    'difficulty': keyword_data.difficulty,
                    'cpc': keyword_data.cpc,
                    'competition': keyword_data.competition,
                    'trend': keyword_data.trend
                })
                all_keywords_data.append(keyword_data)
            
            # Sorteer op zoekvolume
            category_data.sort(key=lambda x: x['search_volume'], reverse=True)
            processed_categories[category] = category_data[:10]  # Top 10 per categorie
        
        # Analyseer opportunities
        opportunities = keyword_tool.analyze_keyword_opportunities(all_keywords_data)
        processed_opportunities = {}
        
        for opp_type, keywords in opportunities.items():
            processed_opportunities[opp_type] = [
                {
                    'keyword': kd.keyword,
                    'search_volume': kd.search_volume,
                    'difficulty': kd.difficulty,
                    'cpc': kd.cpc,
                    'competition': kd.competition,
                    'trend': kd.trend
                } for kd in keywords
            ]
        
        # Statistieken
        total_volume = sum(k.search_volume for k in all_keywords_data)
        avg_difficulty = sum(k.difficulty for k in all_keywords_data) / len(all_keywords_data)
        
        response = {
            'main_keyword': main_keyword,
            'categories': processed_categories,
            'opportunities': processed_opportunities,
            'stats': {
                'total_keywords': len(all_keywords_data),
                'total_volume': total_volume,
                'avg_difficulty': round(avg_difficulty, 1),
                'avg_volume': total_volume // len(all_keywords_data)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export_csv():
    """Export resultaten naar CSV"""
    try:
        data = request.json
        
        # Maak CSV in geheugen
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Category', 'Keyword', 'Search Volume', 'Difficulty', 'CPC', 'Competition', 'Trend'])
        
        # Data
        for category, keywords in data.get('categories', {}).items():
            for keyword_data in keywords:
                writer.writerow([
                    category.replace('_', ' ').title(),
                    keyword_data['keyword'],
                    keyword_data['search_volume'],
                    keyword_data['difficulty'],
                    keyword_data['cpc'],
                    keyword_data['competition'],
                    keyword_data['trend']
                ])
        
        # Maak bestand voor download
        output.seek(0)
        
        # Maak temporary file
        filename = f"keyword_research_{data.get('main_keyword', 'results').replace(' ', '_')}.csv"
        
        # Return CSV als download
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sitemap.xml')
def sitemap():
    """Serve the sitemap index file"""
    try:
        return send_file('sitemap.xml', mimetype='application/xml')
    except Exception as e:
        return f"Error serving sitemap: {str(e)}", 500

@app.route('/robots.txt')
def robots():
    """Serve robots.txt with sitemap reference"""
    robots_content = """User-agent: *
Allow: /

# Sitemap
Sitemap: https://lucy.world/sitemap.xml

# SEO optimizations
Crawl-delay: 1
"""
    return robots_content, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    # Zorg ervoor dat templates directory bestaat
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("🌐 Starting Semantic Keyword Research Web Interface...")
    print("📍 Open http://localhost:5000 in je browser")
    app.run(debug=True, port=5000)