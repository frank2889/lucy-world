#!/bin/bash

# Quick DNS Setup Helper voor search.lucy.world

echo "🌐 Lucy World Search - DNS Setup Helper"
echo "========================================"

# Check if we're on the server
if command -v curl &> /dev/null; then
    echo ""
    echo "📍 Je server externe IP adres:"
    EXTERNAL_IP=$(curl -s -4 icanhazip.com)
    echo "   $EXTERNAL_IP"
    echo ""
    echo "🔧 DNS Setup:"
    echo "   1. Ga naar je domain provider (waar lucy.world geregistreerd is)"
    echo "   2. Voeg een A Record toe:"
    echo "      Type: A"
    echo "      Name: search"
    echo "      Value: $EXTERNAL_IP"
    echo "      TTL: 300"
    echo ""
fi

echo "🔍 DNS Status Check:"
echo "===================="

# Check if dig is available
if command -v dig &> /dev/null; then
    echo "Checking DNS resolution..."
    
    # Check Google DNS
    GOOGLE_DNS=$(dig +short search.lucy.world @8.8.8.8 2>/dev/null)
    if [ -n "$GOOGLE_DNS" ]; then
        echo "✅ Google DNS (8.8.8.8): $GOOGLE_DNS"
    else
        echo "❌ Google DNS (8.8.8.8): No resolution"
    fi
    
    # Check Cloudflare DNS
    CLOUDFLARE_DNS=$(dig +short search.lucy.world @1.1.1.1 2>/dev/null)
    if [ -n "$CLOUDFLARE_DNS" ]; then
        echo "✅ Cloudflare DNS (1.1.1.1): $CLOUDFLARE_DNS"
    else
        echo "❌ Cloudflare DNS (1.1.1.1): No resolution"
    fi
    
    # Check local DNS
    LOCAL_DNS=$(dig +short search.lucy.world 2>/dev/null)
    if [ -n "$LOCAL_DNS" ]; then
        echo "✅ Local DNS: $LOCAL_DNS"
    else
        echo "❌ Local DNS: No resolution"
    fi
    
else
    echo "⚠️  dig not available, using nslookup..."
    nslookup search.lucy.world 2>/dev/null || echo "❌ DNS not resolved yet"
fi

echo ""
echo "🔐 SSL Certificate Check:"
echo "========================="

# Check if SSL certificate exists
if [ -f "/etc/letsencrypt/live/search.lucy.world/fullchain.pem" ]; then
    echo "✅ SSL Certificate exists"
    
    # Check certificate expiry
    if command -v openssl &> /dev/null; then
        EXPIRY=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/search.lucy.world/fullchain.pem 2>/dev/null | cut -d= -f2)
        echo "   Expires: $EXPIRY"
    fi
else
    echo "❌ SSL Certificate not found"
    echo "   Run: sudo certbot --nginx -d search.lucy.world --email frank@lucy.world --agree-tos --non-interactive"
fi

echo ""
echo "🚀 Service Status Check:"
echo "========================"

# Check services
if systemctl is-active --quiet lucy-world-search; then
    echo "✅ Lucy World Search service is running"
else
    echo "❌ Lucy World Search service is not running"
    echo "   Run: sudo systemctl start lucy-world-search"
fi

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx service is running"
else
    echo "❌ Nginx service is not running"
    echo "   Run: sudo systemctl start nginx"
fi

echo ""
echo "🌐 Website Test:"
echo "================"

# Test website if DNS is working
if [ -n "$LOCAL_DNS" ] || [ -n "$GOOGLE_DNS" ]; then
    echo "Testing website connectivity..."
    
    # Test HTTP (should redirect to HTTPS)
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://search.lucy.world 2>/dev/null || echo "000")
    if [ "$HTTP_STATUS" = "301" ] || [ "$HTTP_STATUS" = "302" ]; then
        echo "✅ HTTP redirects to HTTPS (Status: $HTTP_STATUS)"
    else
        echo "⚠️  HTTP Status: $HTTP_STATUS"
    fi
    
    # Test HTTPS
    HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://search.lucy.world 2>/dev/null || echo "000")
    if [ "$HTTPS_STATUS" = "200" ]; then
        echo "✅ HTTPS working (Status: $HTTPS_STATUS)"
    else
        echo "❌ HTTPS Status: $HTTPS_STATUS"
    fi
    
    # Test health endpoint
    HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://search.lucy.world/health 2>/dev/null || echo "000")
    if [ "$HEALTH_STATUS" = "200" ]; then
        echo "✅ Health check working (Status: $HEALTH_STATUS)"
    else
        echo "❌ Health check Status: $HEALTH_STATUS"
    fi
    
else
    echo "❌ DNS not resolved yet - cannot test website"
    echo "   Wait 5-30 minutes for DNS propagation"
fi

echo ""
echo "📋 Next Steps:"
echo "=============="

if [ -z "$LOCAL_DNS" ] && [ -z "$GOOGLE_DNS" ]; then
    echo "1. ⏳ Wait for DNS propagation (5-30 minutes)"
    echo "2. 🔄 Re-run this script to check status"
    echo "3. 🌐 Check DNS propagation: https://www.whatsmydns.net/"
elif [ ! -f "/etc/letsencrypt/live/search.lucy.world/fullchain.pem" ]; then
    echo "1. 🔐 Setup SSL certificate:"
    echo "   sudo certbot --nginx -d search.lucy.world --email frank@lucy.world --agree-tos --non-interactive"
    echo "2. 🔄 Re-run this script to check status"
else
    echo "✅ Everything looks good!"
    echo "🎉 Your website should be live at: https://search.lucy.world"
fi

echo ""