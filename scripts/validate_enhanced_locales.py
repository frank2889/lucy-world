#!/usr/bin/env python3
"""
Validate that all locales have proper enhanced content:
- Localized meta.title, meta.description, meta.keywords
- Valid structured.json with aiSemantic arrays
- Character count validation for descriptions
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANG_DIR = ROOT / 'languages'

def validate_locale(lang_path: Path) -> list[str]:
    """Validate a single language locale and return list of issues"""
    issues = []
    lang_code = lang_path.name
    
    # Check locale.json
    locale_file = lang_path / 'locale.json'
    if not locale_file.exists():
        issues.append(f"Missing locale.json")
        return issues
    
    try:
        with open(locale_file, 'r', encoding='utf-8') as f:
            locale_data = json.load(f)
    except Exception as e:
        issues.append(f"Invalid JSON in locale.json: {e}")
        return issues
    
    strings = locale_data.get('strings', {})
    
    # Check required meta fields
    meta_title = strings.get('meta.title', '')
    meta_desc = strings.get('meta.description', '')
    meta_keywords = strings.get('meta.keywords', '')
    
    if not meta_title or meta_title == 'Lucy World':
        issues.append("meta.title not localized")
    
    if not meta_desc or meta_desc == 'Keyword research made simple with Google data: suggestions, trends, and insights.':
        issues.append("meta.description not localized")
    
    if not meta_keywords or meta_keywords == 'keyword research, SEO, Google Trends, suggestions, search volume':
        issues.append("meta.keywords not localized")
    
    # Check structured.json
    structured_file = lang_path / 'structured.json'
    if not structured_file.exists():
        issues.append("Missing structured.json")
        return issues
    
    try:
        with open(structured_file, 'r', encoding='utf-8') as f:
            structured_data = json.load(f)
    except Exception as e:
        issues.append(f"Invalid JSON in structured.json: {e}")
        return issues
    
    # Validate structured.json content
    graph = structured_data.get('@graph', [])
    found_webpage = False
    
    for node in graph:
        if node.get('@type') == 'WebPage':
            found_webpage = True
            
            # Check description length (should be 140-160 chars for SEO)
            desc = node.get('description', '')
            if len(desc) < 140 or len(desc) > 160:
                issues.append(f"WebPage description length {len(desc)} chars (should be 140-160)")
            
            # Check for aiSemantic array
            ai_semantic = node.get('aiSemantic', [])
            if not isinstance(ai_semantic, list) or len(ai_semantic) != 6:
                issues.append(f"aiSemantic should be array of 6 items, got {len(ai_semantic) if isinstance(ai_semantic, list) else 'not array'}")
            
            # Check if description is still default
            if desc == "Keyword research made simple with Google data: suggestions, trends, and insights.":
                issues.append("WebPage description not localized")
            
            break
    
    if not found_webpage:
        issues.append("No WebPage node found in structured.json")
    
    return issues

def main():
    if not LANG_DIR.exists():
        print("Languages directory not found")
        return 1
    
    total_languages = 0
    languages_with_issues = 0
    total_issues = 0
    
    # Get all language directories
    for lang_path in sorted(LANG_DIR.iterdir()):
        if not lang_path.is_dir() or len(lang_path.name) != 2:
            continue
        
        total_languages += 1
        issues = validate_locale(lang_path)
        
        if issues:
            languages_with_issues += 1
            total_issues += len(issues)
            print(f"\n❌ {lang_path.name}:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print(f"✅ {lang_path.name}")
    
    print(f"\n📊 Summary:")
    print(f"   Total languages: {total_languages}")
    print(f"   Languages with issues: {languages_with_issues}")
    print(f"   Languages valid: {total_languages - languages_with_issues}")
    print(f"   Total issues: {total_issues}")
    
    return 1 if languages_with_issues > 0 else 0

if __name__ == '__main__':
    sys.exit(main())