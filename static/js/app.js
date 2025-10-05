/**
 * PREMIUM KEYWORD RESEARCH TOOL - MAIN JAVASCRIPT
 * Professional keyword research application
 */

class KeywordResearchApp {
    constructor() {
        this.currentResults = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupAnimations();
    }

    bindEvents() {
        // Hero button functionality
        const heroSearchBtn = document.getElementById('heroSearchBtn');
        if (heroSearchBtn) {
            heroSearchBtn.addEventListener('click', () => this.scrollToSearch());
        }

        // Smooth scroll voor "Ons verhaal" link
        const scrollButton = document.querySelector('.scroll-button');
        if (scrollButton) {
            scrollButton.addEventListener('click', (e) => this.handleScrollClick(e));
        }

        // Search functionality
        const searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.performSearch());
        }

        const keywordInput = document.getElementById('keywordInput');
        if (keywordInput) {
            keywordInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
        }

        // Export functionality
        const exportBtn = document.getElementById('exportBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportResults());
        }
    }

    setupAnimations() {
        // Intersection Observer voor scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observeer alle animatable elementen
        const animatableElements = document.querySelectorAll('.stat-card, .category-card, .opportunities');
        animatableElements.forEach(el => observer.observe(el));
    }

    scrollToSearch() {
        const searchSection = document.getElementById('searchSection');
        if (searchSection) {
            searchSection.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
            
            // Focus op input field na scroll
            setTimeout(() => {
                const keywordInput = document.getElementById('keywordInput');
                if (keywordInput) {
                    keywordInput.focus();
                }
            }, 500);
        }
    }

    handleScrollClick(e) {
        e.preventDefault();
        this.scrollToSearch();
    }

    async performSearch() {
        const keywordInput = document.getElementById('keywordInput');
        const keyword = keywordInput?.value.trim();

        if (!keyword) {
            this.showError('Voer een zoekwoord in');
            return;
        }

        this.showLoading(true);
        this.hideError();

        try {
            const response = await fetch('/api/premium/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ keyword: keyword })
            });

            if (!response.ok) {
                throw new Error('Er is een fout opgetreden bij het ophalen van premium data');
            }

            const data = await response.json();
            this.currentResults = data;
            this.displayResults(data);

        } catch (error) {
            console.error('Search error:', error);
            this.showError(error.message);
        } finally {
            this.showLoading(false);
        }
    }

    displayResults(data) {
        // Update statistieken
        this.updateStats(data.stats);

        // Display trends info
        this.displayTrendsInfo(data.trends);

        // Display opportunities
        this.displayOpportunities(data.opportunities);

        // Display categories
        this.displayCategories(data.categories);

        // Toon resultaten met smooth scroll
        const resultsSection = document.getElementById('results');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            setTimeout(() => {
                resultsSection.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 100);
        }
    }

    updateStats(stats) {
        const statElements = {
            'totalKeywords': stats.total_keywords,
            'realDataKeywords': stats.real_data_keywords,
            'totalVolume': stats.total_volume, 
            'avgDifficulty': stats.avg_difficulty + '/100'
        };

        Object.entries(statElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                // Animate numbers
                this.animateNumber(element, value);
            }
        });
    }

    animateNumber(element, finalValue) {
        const isNumber = typeof finalValue === 'number';
        const duration = 1000;
        const steps = 30;
        const stepValue = isNumber ? finalValue / steps : 0;
        let currentStep = 0;

        const interval = setInterval(() => {
            currentStep++;
            
            if (isNumber) {
                const currentValue = Math.round(stepValue * currentStep);
                element.textContent = currentValue.toLocaleString();
            } else {
                element.textContent = finalValue;
            }

            if (currentStep >= steps) {
                clearInterval(interval);
                element.textContent = isNumber ? finalValue.toLocaleString() : finalValue;
            }
        }, duration / steps);
    }

    displayTrendsInfo(trends) {
        const trendsInfo = document.getElementById('trendsInfo');
        const trendsContent = document.getElementById('trendsContent');
        
        if (trends.data_points > 0 && trendsInfo && trendsContent) {
            trendsInfo.style.display = 'block';
            trendsContent.innerHTML = `
                <p>📊 Gemiddelde interesse: <strong>${trends.avg_interest.toFixed(1)}/100</strong></p>
                <p>📈 Trend richting: <strong>${trends.trend_direction}</strong></p>
                <p>📅 Data punten: <strong>${trends.data_points} (12 maanden)</strong></p>
            `;
        }
    }

    displayOpportunities(opportunities) {
        const grid = document.getElementById('opportunitiesGrid');
        if (!grid) return;

        grid.innerHTML = '';

        const oppTitles = {
            'high_volume': '🔥 Hoog Volume',
            'low_competition': '🟢 Lage Competitie', 
            'real_data': '✅ Echte Data',
            'commercial': '💰 Commercieel'
        };

        Object.entries(opportunities).forEach(([type, keywords]) => {
            if (keywords.length === 0) return;

            const section = document.createElement('div');
            section.className = 'opp-section';
            section.innerHTML = `
                <h4>${oppTitles[type] || type}</h4>
                ${keywords.slice(0, 5).map(kw => `
                    <div class="keyword-item">
                        <span class="keyword-name">${kw.keyword}</span>
                        <div class="keyword-metrics">
                            <span class="metric ${this.getVolumeClass(kw.search_volume)}">
                                📈 ${kw.search_volume.toLocaleString()}
                            </span>
                            <span class="source-badge ${kw.source === 'Real Data' ? 'source-real' : 'source-generated'}">
                                ${kw.source === 'Real Data' ? 'ECHT' : 'GEN'}
                            </span>
                        </div>
                    </div>
                `).join('')}
            `;
            grid.appendChild(section);
        });
    }

    displayCategories(categories) {
        const grid = document.getElementById('categoriesGrid');
        if (!grid) return;

        grid.innerHTML = '';

        const categoryTitles = {
            'google_suggestions': '🔍 Google Autocomplete',
            'trends_related': '📈 Google Trends Gerelateerd',
            'related_questions': '❓ Gerelateerde Vragen',
            'wikipedia_terms': '📚 Wikipedia Gerelateerd'
        };

        Object.entries(categories).forEach(([category, keywords]) => {
            if (keywords.length === 0) return;

            const isRealData = category === 'google_suggestions' || category === 'trends_related';

            const card = document.createElement('div');
            card.className = 'category-card';
            card.innerHTML = `
                <div class="category-header">
                    <span>${categoryTitles[category] || category}</span>
                    ${isRealData ? '<span class="real-data-badge">ECHTE DATA</span>' : ''}
                </div>
                <div class="category-content">
                    ${keywords.map(kw => `
                        <div class="keyword-item">
                            <span class="keyword-name">${kw.keyword}</span>
                            <div class="keyword-metrics">
                                <span class="metric ${this.getVolumeClass(kw.search_volume)}">
                                    ${this.getVolumeEmoji(kw.search_volume)} ${kw.search_volume.toLocaleString()}
                                </span>
                                <span class="metric ${this.getDifficultyClass(kw.difficulty)}">
                                    ${this.getDifficultyEmoji(kw.difficulty)} ${kw.difficulty}/100
                                </span>
                                <span class="source-badge ${kw.source === 'Real Data' ? 'source-real' : 'source-generated'}">
                                    ${kw.source === 'Real Data' ? 'ECHT' : 'GEN'}
                                </span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            grid.appendChild(card);
        });
    }

    // Utility methods voor styling
    getVolumeClass(volume) {
        if (volume > 5000) return 'volume-high';
        if (volume > 2000) return 'volume-medium';
        return 'volume-low';
    }

    getDifficultyClass(difficulty) {
        if (difficulty < 40) return 'difficulty-low';
        if (difficulty < 70) return 'difficulty-medium';
        return 'difficulty-high';
    }

    getVolumeEmoji(volume) {
        if (volume > 5000) return '🔥';
        if (volume > 2000) return '📈';
        return '📊';
    }

    getDifficultyEmoji(difficulty) {
        if (difficulty < 40) return '🟢';
        if (difficulty < 70) return '🟡';
        return '🔴';
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const searchBtn = document.getElementById('searchBtn');
        const results = document.getElementById('results');

        if (loading) loading.style.display = show ? 'block' : 'none';
        if (searchBtn) searchBtn.disabled = show;
        if (results) {
            results.style.display = show ? 'none' : (this.currentResults ? 'block' : 'none');
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            
            // Auto hide error after 5 seconds
            setTimeout(() => this.hideError(), 5000);
        }
    }

    hideError() {
        const errorDiv = document.getElementById('error');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    async exportResults() {
        if (!this.currentResults) {
            this.showError('Geen resultaten om te exporteren');
            return;
        }

        try {
            const response = await fetch('/api/premium/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.currentResults)
            });

            if (!response.ok) {
                throw new Error('Premium export mislukt');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `premium_keyword_research_${this.currentResults.main_keyword.replace(/\s+/g, '_')}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Show success message
            this.showTemporaryMessage('✅ CSV succesvol gedownload!', 'success');

        } catch (error) {
            console.error('Export error:', error);
            this.showError('Premium export mislukt: ' + error.message);
        }
    }

    showTemporaryMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `temp-message temp-message-${type}`;
        messageDiv.textContent = message;
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#28a745' : '#ff6b35'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 9999;
            font-weight: 600;
            animation: slideInRight 0.3s ease;
        `;

        document.body.appendChild(messageDiv);

        setTimeout(() => {
            messageDiv.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new KeywordResearchApp();
});

// Add slide animations for temporary messages
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }

    .animate-in {
        animation: fadeInUp 0.6s ease forwards;
    }
`;
document.head.appendChild(style);