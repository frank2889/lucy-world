#!/usr/bin/env python3
"""
Free Web Interface voor Semantic Keyword Research Tool
Een Flask webapplicatie die 100% gratis keyword data gebruikt
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import csv
import io
from free_keyword_tool import FreeKeywordTool
import os
from datetime import datetime

app = Flask(__name__)

# Initialiseer de gratis keyword tool
keyword_tool = FreeKeywordTool()

@app.route('/')
def index():
    """Hoofdpagina van de Canva-stijl web interface"""
    return render_template('canva_index.html')

@app.route('/search', methods=['POST'])
def search_keywords():
    """Nieuwe zoek endpoint voor de Canva-stijl interface"""
    try:
        keyword = request.form.get('keyword', '').strip()
        language = request.form.get('language', '').strip().lower() or keyword_tool.default_language
        
        if not keyword:
            return jsonify({'error': 'Geen zoekwoord opgegeven'}), 400
        
        # Voer gratis keyword research uit
        raw_keyword_data = keyword_tool.research_comprehensive(keyword, language=language)
        processed_keywords = keyword_tool.process_keywords_with_data(
            raw_keyword_data,
            keyword,
            language=language,
            country=request.form.get('country', 'NL').upper() if request.form else 'NL',
        )

        trends_data = raw_keyword_data.get('trends_data', {})
        interest_points = trends_data.get('interest', [])

        response_data = {
            'keyword': keyword,
            'language': language,
            'categories': {},
            'trends': {
                'avg_interest': (sum(interest_points) / len(interest_points)) if interest_points else 0,
                'trend_direction': trends_data.get('trend_direction', 'Stable'),
                'data_points': len(interest_points)
            },
            'summary': {
                'total_keywords': 0,
                'total_volume': 0,
                'real_data_keywords': 0
            }
        }

        total_volume = 0
        total_keywords = 0
        real_data_count = 0

        for category, keywords in processed_keywords.items():
            response_data['categories'][category] = []
            for kd in keywords:
                response_data['categories'][category].append({
                    'keyword': kd.keyword,
                    'search_volume': kd.search_volume,
                    'difficulty': kd.difficulty,
                    'cpc': kd.cpc,
                    'competition': kd.competition,
                    'trend': kd.trend,
                    'source': kd.source
                })
                total_volume += kd.search_volume
                total_keywords += 1
                if kd.source == "Real Data":
                    real_data_count += 1

        response_data['summary']['total_keywords'] = total_keywords
        response_data['summary']['total_volume'] = total_volume
        response_data['summary']['real_data_keywords'] = real_data_count
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research-free', methods=['POST'])
def research_keywords_free():
    """API endpoint voor gratis keyword research"""
    try:
        data = request.json
        main_keyword = data.get('keyword', '').strip()
        language = (data.get('language') or keyword_tool.default_language or 'nl').lower()
        
        if not main_keyword:
            return jsonify({'error': 'Geen zoekwoord opgegeven'}), 400
        
        # Voer gratis keyword research uit
        raw_keyword_data = keyword_tool.research_comprehensive(main_keyword, language=language)
        processed_data = keyword_tool.process_keywords_with_data(
            raw_keyword_data,
            main_keyword,
            language=language,
            country=(data.get('country') or 'NL').upper() if isinstance(data, dict) else 'NL',
        )
        
        # Converteer naar JSON-serializeerbare format
        json_categories = {}
        all_keywords_data = []
        
        for category, keywords in processed_data.items():
            json_keywords = []
            for kd in keywords:
                keyword_dict = {
                    'keyword': kd.keyword,
                    'search_volume': kd.search_volume,
                    'difficulty': kd.difficulty,
                    'cpc': kd.cpc,
                    'competition': kd.competition,
                    'trend': kd.trend,
                    'source': kd.source
                }
                json_keywords.append(keyword_dict)
                all_keywords_data.append(kd)
            
            json_categories[category] = json_keywords
        
        # Analyseer opportunities (vereenvoudigd voor web)
        opportunities = {
            'high_volume': [k for k in all_keywords_data if k.search_volume > 5000],
            'low_competition': [k for k in all_keywords_data if k.difficulty < 40],
            'real_data': [k for k in all_keywords_data if k.source == "Real Data"],
            'commercial': [k for k in all_keywords_data if any(word in k.keyword.lower() 
                         for word in ['kopen', 'bestellen', 'huren', 'boeken'])]
        }
        
        # Converteer opportunities naar JSON
        json_opportunities = {}
        for opp_type, keywords in opportunities.items():
            json_opportunities[opp_type] = [
                {
                    'keyword': kd.keyword,
                    'search_volume': kd.search_volume,
                    'difficulty': kd.difficulty,
                    'cpc': kd.cpc,
                    'competition': kd.competition,
                    'trend': kd.trend,
                    'source': kd.source
                } for kd in sorted(keywords, key=lambda x: x.search_volume, reverse=True)[:5]
            ]
        
        # Trends data
        trends_data = raw_keyword_data.get('trends_data', {})
        
        # Statistieken
        total_volume = sum(k.search_volume for k in all_keywords_data)
        avg_difficulty = sum(k.difficulty for k in all_keywords_data) / len(all_keywords_data) if all_keywords_data else 0
        real_data_count = sum(1 for k in all_keywords_data if k.source == "Real Data")
        
        response = {
            'main_keyword': main_keyword,
            'language': language,
            'categories': json_categories,
            'opportunities': json_opportunities,
            'trends': {
                'avg_interest': sum(trends_data.get('interest', [])) / len(trends_data.get('interest', [])) if trends_data.get('interest') else 0,
                'trend_direction': trends_data.get('trend_direction', 'Stable'),
                'data_points': len(trends_data.get('interest', []))
            },
            'stats': {
                'total_keywords': len(all_keywords_data),
                'real_data_keywords': real_data_count,
                'total_volume': total_volume,
                'avg_difficulty': round(avg_difficulty, 1),
                'avg_volume': total_volume // len(all_keywords_data) if all_keywords_data else 0,
                'cost': 0.00  # Altijd gratis!
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-free', methods=['POST'])
def export_csv_free():
    """Export gratis resultaten naar CSV"""
    try:
        data = request.json
        
        # Maak CSV in geheugen
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header met extra info
        writer.writerow(['Category', 'Keyword', 'Search Volume', 'Difficulty', 'CPC', 'Competition', 'Trend', 'Data Source'])
        
        # Data
        for category, keywords in data.get('categories', {}).items():
            category_name = {
                'google_suggestions': 'Google Autocomplete',
                'trends_related': 'Google Trends Related',
                'related_questions': 'Generated Questions',
                'wikipedia_terms': 'Wikipedia Related'
            }.get(category, category.title())
            
            for keyword_data in keywords:
                writer.writerow([
                    category_name,
                    keyword_data['keyword'],
                    keyword_data['search_volume'],
                    keyword_data['difficulty'],
                    keyword_data['cpc'],
                    keyword_data['competition'],
                    keyword_data['trend'],
                    keyword_data['source']
                ])
        
        # Maak bestand voor download
        output.seek(0)
        filename = f"free_keyword_research_{data.get('main_keyword', 'results').replace(' ', '_')}.csv"
        
        # Return CSV als download
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🆓 Starting FREE Semantic Keyword Research Web Interface...")
    print("💰 100% Gratis data van Google Trends, Google Suggest & Wikipedia")
    print("📍 Open http://localhost:5000 in je browser")
    app.run(debug=True, host='0.0.0.0', port=5001)