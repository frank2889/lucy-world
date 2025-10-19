#!/usr/bin/env python3
"""
Sitemap Verification Script for Lucy World Search
Verifies all sitemaps and generates a summary
"""

import os
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import requests

def verify_sitemap_index(sitemap_path):
    """Verify the main sitemap index"""
    print("🗺️  SITEMAP INDEX VERIFICATION")
    print("=" * 50)
    
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # Count sitemaps
        sitemaps = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
        print(f"✅ Sitemap index found: {len(sitemaps)} language sitemaps")
        
        # Show first few entries
        print("\n📋 Sample entries:")
        for i, sitemap in enumerate(sitemaps[:5]):
            loc = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            lastmod = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            if loc is not None:
                print(f"   {i+1}. {loc.text}")
        
        print(f"   ... and {len(sitemaps)-5} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading sitemap index: {e}")
        return False

def verify_language_sitemaps():
    """Verify individual language sitemaps exist"""
    print("\n🌍 LANGUAGE SITEMAPS VERIFICATION")
    print("=" * 50)
    
    languages_dir = "languages"
    if not os.path.exists(languages_dir):
        print("❌ Languages directory not found")
        return False
    
    # Get all language directories
    lang_dirs = [d for d in os.listdir(languages_dir) 
                 if os.path.isdir(os.path.join(languages_dir, d))]
    
    existing_sitemaps = 0
    missing_sitemaps = []
    
    for lang in sorted(lang_dirs):
        sitemap_path = os.path.join(languages_dir, lang, "sitemap.xml")
        if os.path.exists(sitemap_path):
            existing_sitemaps += 1
        else:
            missing_sitemaps.append(lang)
    
    print(f"✅ Found {existing_sitemaps} language sitemaps")
    print(f"📊 Total languages: {len(lang_dirs)}")
    
    if missing_sitemaps:
        print(f"⚠️  Missing sitemaps for: {', '.join(missing_sitemaps[:10])}")
        if len(missing_sitemaps) > 10:
            print(f"   ... and {len(missing_sitemaps)-10} more")
    
    return len(missing_sitemaps) == 0

def generate_sitemap_summary():
    """Generate a summary report"""
    print("\n📊 SITEMAP SUMMARY REPORT")
    print("=" * 50)
    
    # Check main files
    files_to_check = [
        ("sitemap.xml", "Main sitemap index"),
        ("robots.txt", "Robots.txt file"),
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {description}: {filename} ({size:,} bytes)")
        else:
            print(f"❌ {description}: {filename} (missing)")
    
    # Count total URLs across all sitemaps
    total_urls = 0
    languages_dir = "languages"
    
    if os.path.exists(languages_dir):
        for lang in os.listdir(languages_dir):
            sitemap_path = os.path.join(languages_dir, lang, "sitemap.xml")
            if os.path.exists(sitemap_path):
                try:
                    tree = ET.parse(sitemap_path)
                    root = tree.getroot()
                    urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                    total_urls += len(urls)
                except:
                    pass
    
    print(f"🔗 Total URLs across all sitemaps: {total_urls:,}")
    
    # SEO recommendations
    print(f"\n🚀 SEO RECOMMENDATIONS")
    print("=" * 50)
    print("✅ Submit sitemap to Google Search Console:")
    print("   https://search.google.com/search-console")
    print("✅ Submit sitemap to Bing Webmaster Tools:")
    print("   https://www.bing.com/webmasters")
    print("✅ Monitor sitemap in GTM for crawling stats")
    print("✅ Set up GSC API to track clicks & impressions")

def main():
    print("🔍 LUCY WORLD SEARCH - SITEMAP VERIFICATION")
    print("=" * 60)
    
    # Verify main sitemap
    sitemap_valid = verify_sitemap_index("sitemap.xml")
    
    # Verify language sitemaps
    lang_sitemaps_valid = verify_language_sitemaps()
    
    # Generate summary
    generate_sitemap_summary()
    
    # Final status
    print(f"\n🎯 FINAL STATUS")
    print("=" * 50)
    if sitemap_valid and lang_sitemaps_valid:
        print("🎉 All sitemaps verified successfully!")
        print("🌐 Ready for search engine submission!")
    else:
        print("⚠️  Some issues found - check details above")

if __name__ == "__main__":
    main()