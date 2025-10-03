/**
 * GTM Event Tracking for Lucy World Search
 * Tracks keyword research interactions and user behavior
 */

// Initialize dataLayer if not exists
window.dataLayer = window.dataLayer || [];

/**
 * Push custom events to GTM dataLayer
 */
function gtmTrack(event, data = {}) {
    window.dataLayer.push({
        event: event,
        timestamp: new Date().toISOString(),
        ...data
    });
    console.log('📊 GTM Event:', event, data);
}

/**
 * Track keyword searches
 */
function trackKeywordSearch(keyword, tool_type = 'semantic') {
    gtmTrack('keyword_search', {
        search_keyword: keyword,
        tool_type: tool_type,
        search_length: keyword.length
    });
}

/**
 * Track tool usage
 */
function trackToolUsage(tool_name, action = 'used') {
    gtmTrack('tool_interaction', {
        tool_name: tool_name,
        action: action,
        page_url: window.location.href
    });
}

/**
 * Track result interactions
 */
function trackResultClick(keyword, result_type = 'suggestion') {
    gtmTrack('result_click', {
        clicked_keyword: keyword,
        result_type: result_type,
        position: arguments[2] || null
    });
}

/**
 * Track downloads/exports
 */
function trackExport(format, keyword_count) {
    gtmTrack('data_export', {
        export_format: format,
        keyword_count: keyword_count,
        export_time: new Date().toISOString()
    });
}

/**
 * Track page engagement
 */
function trackEngagement(action, value = null) {
    gtmTrack('user_engagement', {
        engagement_action: action,
        engagement_value: value,
        session_time: Date.now() - window.sessionStart || 0
    });
}

/**
 * Track scroll depth (useful for content analysis)
 */
function trackScrollDepth() {
    const scrollPercent = Math.round(
        (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
    );
    
    if (scrollPercent >= 25 && !window.scroll25) {
        window.scroll25 = true;
        gtmTrack('scroll_depth', { depth: '25%' });
    }
    if (scrollPercent >= 50 && !window.scroll50) {
        window.scroll50 = true;
        gtmTrack('scroll_depth', { depth: '50%' });
    }
    if (scrollPercent >= 75 && !window.scroll75) {
        window.scroll75 = true;
        gtmTrack('scroll_depth', { depth: '75%' });
    }
    if (scrollPercent >= 90 && !window.scroll90) {
        window.scroll90 = true;
        gtmTrack('scroll_depth', { depth: '90%' });
    }
}

/**
 * Initialize tracking when page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    window.sessionStart = Date.now();
    
    // Track page view
    gtmTrack('page_view', {
        page_title: document.title,
        page_url: window.location.href,
        referrer: document.referrer
    });
    
    // Set up scroll tracking
    window.addEventListener('scroll', trackScrollDepth);
    
    // Set up search button click tracking
    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            const keyword = document.getElementById('keywordInput')?.value?.trim() || '';
            
            // Track search button click
            gtmTrack('search_button_click', {
                search_keyword: keyword,
                button_id: 'searchBtn',
                button_text: this.textContent,
                keyword_length: keyword.length,
                has_keyword: keyword.length > 0
            });
            
            console.log('🔍 Search button clicked:', keyword);
        });
    }
    
    // Set up export button click tracking
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            gtmTrack('export_button_click', {
                button_id: 'exportBtn',
                button_text: this.textContent,
                has_results: !!window.currentResults
            });
            
            console.log('📊 Export button clicked');
        });
    }
    
    // Track input focus (user engagement)
    const keywordInput = document.getElementById('keywordInput');
    if (keywordInput) {
        keywordInput.addEventListener('focus', function() {
            gtmTrack('search_input_focus', {
                input_id: 'keywordInput',
                current_value: this.value
            });
        });
        
        // Track when user starts typing
        let typingTimer;
        keywordInput.addEventListener('input', function() {
            clearTimeout(typingTimer);
            typingTimer = setTimeout(() => {
                if (this.value.length >= 3) {
                    gtmTrack('search_input_typing', {
                        keyword_partial: this.value,
                        keyword_length: this.value.length
                    });
                }
            }, 1000); // Wait 1 second after user stops typing
        });
    }
    
    // Track time on page
    window.addEventListener('beforeunload', function() {
        const timeOnPage = Date.now() - window.sessionStart;
        gtmTrack('session_end', {
            time_on_page: Math.round(timeOnPage / 1000), // seconds
            page_url: window.location.href
        });
    });
});

// Export functions for global use
window.lucyAnalytics = {
    trackKeywordSearch,
    trackToolUsage,
    trackResultClick,
    trackExport,
    trackEngagement,
    gtmTrack
};