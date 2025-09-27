#!/usr/bin/env python3
"""
Production Flask Application voor Lucy World Search
Hoofd applicatie die alle keyword tools combineert voor deployment
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import json
import csv
import io
import os
from datetime import datetime
from advanced_keyword_tool import AdvancedKeywordTool
from free_keyword_tool import FreeKeywordTool
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

# Configure logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Trust proxy headers from the DigitalOcean load balancer so request.scheme is correct
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

# Security: prefer HTTPS for generated URLs and secure cookies in production
app.config.update(
    PREFERRED_URL_SCHEME="https",
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# Initialiseer beide keyword tools
try:
    advanced_tool = AdvancedKeywordTool()
    free_tool = FreeKeywordTool()
    logger.info("Keyword tools successfully initialized")
except Exception as e:
    logger.error(f"Error initializing keyword tools: {e}")
    advanced_tool = None
    free_tool = None

@app.route('/')
def index():
    """Hoofdpagina - toon gratis tool direct"""
    return render_template('canva_index.html')

@app.route('/search', methods=['GET', 'POST'])
def search_index():
    """Search pagina (GET) of gratis zoekactie (POST)."""
    if request.method == 'POST':
        # Reuse the free API logic so canva_index.html can POST to /search
        return free_search_keywords()
    # GET -> redirect to free UI
    return redirect('/search/free')

@app.route('/search/free')
def free_index():
    """Gratis keyword research tool"""
    return render_template('canva_index.html')

@app.route('/search/advanced')
def advanced_index():
    """Geavanceerde keyword research tool"""
    return render_template('index.html')

@app.route('/search/scale')
def scale_index():
    """Scale pagina"""
    return render_template('scale_index.html')

# ============================================================================
# FREE KEYWORD RESEARCH ENDPOINTS
# ============================================================================

@app.route('/api/free/search', methods=['POST'])
def free_search_keywords():
    """Gratis keyword research API"""
    try:
        if not free_tool:
            return jsonify({'error': 'Free keyword tool niet beschikbaar'}), 500
            
        data = request.get_json() or {}
        keyword = data.get('keyword', request.form.get('keyword', '')).strip()
        language = data.get('language', request.form.get('language', '')).strip().lower()
        
        if not keyword:
            return jsonify({'error': 'Geen zoekwoord opgegeven'}), 400
        
        if not language:
            language = free_tool.default_language
        
        logger.info(f"Free search for keyword: {keyword}, language: {language}")
        
        # Voer gratis keyword research uit
        raw_keyword_data = free_tool.research_comprehensive(keyword, language=language)
        processed_keywords = free_tool.process_keywords_with_data(
            raw_keyword_data,
            keyword,
            language=language,
        )

        trends_data = raw_keyword_data.get('trends_data', {})
        interest_points = trends_data.get('interest', [])

        # Trends summary
        avg_interest = round(sum(interest_points) / len(interest_points), 1) if interest_points else 0
        trend_direction = trends_data.get('trend_direction', 'Stable')

        response_data = {
            'keyword': keyword,
            'language': language,
            'categories': {},
            'trends': {
                'interest_over_time': interest_points,
                'trending_searches': trends_data.get('trending_searches', []),
                'related_topics': trends_data.get('related_topics', []),
                'avg_interest': avg_interest,
                'trend_direction': trend_direction,
                'data_points': len(interest_points)
            },
            'stats': {
                'total_keywords': 0,
                'categories_count': 0
            },
            # UI expects a summary block
            'summary': {
                'total_volume': 0,
                'total_keywords': 0,
                'real_data_keywords': 0
            },
            'timestamp': datetime.now().isoformat()
        }

        # Verwerk alle categorieën
        total_keywords = 0
        total_volume = 0
        real_data_keywords = 0
        for category, keywords in processed_keywords.items():
            if keywords:
                category_data = []
                for kw in keywords[:20]:  # Limit to top 20
                    # kw may be a dataclass object (KeywordData) or dict
                    if hasattr(kw, 'keyword'):
                        item = {
                            'keyword': getattr(kw, 'keyword', ''),
                            'search_volume': getattr(kw, 'search_volume', 0),
                            'difficulty': getattr(kw, 'difficulty', None),
                            'cpc': getattr(kw, 'cpc', None),
                            'competition': getattr(kw, 'competition', 'Unknown'),
                            'trend': getattr(kw, 'trend', trend_direction),
                            'source': getattr(kw, 'source', None),
                        }
                    else:
                        item = {
                            'keyword': kw.get('keyword', ''),
                            'search_volume': kw.get('search_volume', kw.get('volume', 0)),
                            'difficulty': kw.get('difficulty'),
                            'cpc': kw.get('cpc'),
                            'competition': kw.get('competition', 'Unknown'),
                            'trend': kw.get('trend', trend_direction),
                            'source': kw.get('source')
                        }
                    category_data.append(item)
                    total_volume += int(item.get('search_volume') or 0)
                    if (item.get('source') == 'Real Data'):
                        real_data_keywords += 1
                
                response_data['categories'][category] = category_data
                total_keywords += len(category_data)

        response_data['stats']['total_keywords'] = total_keywords
        response_data['stats']['categories_count'] = len(response_data['categories'])
        response_data['summary']['total_keywords'] = total_keywords
        response_data['summary']['total_volume'] = total_volume
        response_data['summary']['real_data_keywords'] = real_data_keywords

        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in free search: {e}")
        return jsonify({'error': f'Er is een fout opgetreden: {str(e)}'}), 500

# ============================================================================
# ADVANCED KEYWORD RESEARCH ENDPOINTS
# ============================================================================

@app.route('/api/advanced/research', methods=['POST'])
def advanced_research_keywords():
    """Geavanceerde keyword research API"""
    try:
        if not advanced_tool:
            return jsonify({'error': 'Advanced keyword tool niet beschikbaar'}), 500
            
        data = request.json
        main_keyword = data.get('keyword', '').strip()
        
        if not main_keyword:
            return jsonify({'error': 'Geen zoekwoord opgegeven'}), 400
        
        logger.info(f"Advanced search for keyword: {main_keyword}")
        
        # Voer keyword research uit
        keyword_categories = advanced_tool.get_comprehensive_keywords(main_keyword)
        
        # Verwerk alle keywords
        all_keywords_data = []
        processed_categories = {}
        
        for category, keywords in keyword_categories.items():
            category_data = []
            for keyword in keywords:
                keyword_data = advanced_tool.get_search_volume_advanced(keyword)
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
        opportunities = advanced_tool.analyze_keyword_opportunities(all_keywords_data)
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
        avg_difficulty = sum(k.difficulty for k in all_keywords_data) / len(all_keywords_data) if all_keywords_data else 0
        
        response = {
            'main_keyword': main_keyword,
            'categories': processed_categories,
            'opportunities': processed_opportunities,
            'stats': {
                'total_keywords': len(all_keywords_data),
                'total_volume': total_volume,
                'avg_difficulty': round(avg_difficulty, 1),
                'avg_volume': total_volume // len(all_keywords_data) if all_keywords_data else 0
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in advanced research: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@app.route('/api/export/csv', methods=['POST'])
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
                    keyword_data.get('keyword', ''),
                    keyword_data.get('search_volume', keyword_data.get('volume', 0)),
                    keyword_data.get('difficulty', ''),
                    keyword_data.get('cpc', ''),
                    keyword_data.get('competition', ''),
                    keyword_data.get('trend', '')
                ])
        
        # Maak bestand voor download
        output.seek(0)
        
        # Maak temporary file
        filename = f"keyword_research_{data.get('main_keyword', data.get('keyword', 'results')).replace(' ', '_')}.csv"
        
        # Return CSV als download
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error in CSV export: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.route('/health')
def health_check():
    """Health check voor load balancer"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'tools': {
            'advanced': advanced_tool is not None,
            'free': free_tool is not None
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint niet gevonden'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Interne server fout'}), 500

# Add HSTS over HTTPS responses (does not affect health checks or HTTP traffic)
@app.after_request
def add_security_headers(response):
    try:
        # Only set HSTS on secure requests so we don't interfere with internal health checks
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    except Exception:
        pass
    return response

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Lucy World Search on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)