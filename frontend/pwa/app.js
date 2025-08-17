// AgriSage PWA JavaScript
class AgriSageApp {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.isOffline = false;
        this.initializeElements();
        this.bindEvents();
        this.loadWelcomeMessage();
    }

    initializeElements() {
        this.messagesContainer = document.getElementById('messages');
        this.questionInput = document.getElementById('questionInput');
        this.sendButton = document.getElementById('sendButton');
        this.locationInput = document.getElementById('locationInput');
        this.offlineToggle = document.getElementById('offlineMode');
        this.loadingDiv = document.getElementById('loading');
    }

    bindEvents() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.offlineToggle.addEventListener('change', (e) => {
            this.isOffline = e.target.checked;
            this.showMessage('system', 
                this.isOffline ? 
                '📱 Offline mode enabled - using local rules' : 
                '🌐 Online mode enabled - using AI assistant'
            );
        });
    }

    loadWelcomeMessage() {
        // Welcome message is already in HTML
    }

    async sendMessage() {
        const question = this.questionInput.value.trim();
        if (!question) return;

        const location = this.locationInput.value.trim();
        
        // Show user message
        this.showMessage('user', question);
        this.questionInput.value = '';
        
        // Show loading
        this.setLoading(true);
        
        try {
            let response;
            if (this.isOffline) {
                response = await this.getOfflineResponse(question, location);
            } else {
                response = await this.getOnlineResponse(question, location);
            }
            
            this.showBotResponse(response);
        } catch (error) {
            console.error('Error:', error);
            this.showMessage('bot', 
                '❌ Sorry, I encountered an error. Please try again or switch to offline mode.',
                { confidence: 0, escalate: true }
            );
        } finally {
            this.setLoading(false);
        }
    }

    async getOnlineResponse(question, location) {
        const response = await fetch(`${this.apiUrl}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: 'pwa_user',
                question: question,
                location: location || null
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();
    }

    async getOfflineResponse(question, location) {
        // Simple offline rules simulation
        const questionLower = question.toLowerCase();
        
        // Safety check
        const riskyKeywords = ['pesticide', 'insecticide', 'dose', 'spray', 'chemical'];
        if (riskyKeywords.some(keyword => questionLower.includes(keyword))) {
            return {
                answer: "⚠️ This question involves chemicals or dosages. Please consult your local agricultural extension officer or Krishi Vigyan Kendra for safe recommendations.",
                confidence: 1.0,
                provenance: [],
                escalate: true,
                fallback_used: true
            };
        }

        // Irrigation advice
        if (questionLower.includes('irrigat') || questionLower.includes('water')) {
            return {
                answer: "🚿 For irrigation timing:\n• Check soil moisture - if dry 2-3 inches deep, irrigate\n• Avoid irrigation if heavy rain expected (>70% chance)\n• Best time: Early morning or evening\n• Water deeply but less frequently",
                confidence: 0.85,
                provenance: [{ source: "offline_rules", content: "Basic irrigation guidelines" }],
                fallback_used: true
            };
        }

        // Fertilizer advice
        if (questionLower.includes('fertiliz') || questionLower.includes('nutrient')) {
            return {
                answer: "🌱 For fertilizer recommendations:\n• Get soil test done first\n• Apply based on crop growth stage\n• Use balanced NPK for most crops\n• Consult agricultural officer for specific doses",
                confidence: 0.75,
                provenance: [{ source: "offline_rules", content: "General fertilizer guidelines" }],
                fallback_used: true
            };
        }

        // Market advice
        if (questionLower.includes('price') || questionLower.includes('market')) {
            return {
                answer: "💰 For market decisions:\n• Check current mandi prices\n• Compare with last week's rates\n• Consider storage costs vs immediate sale\n• Sell when prices are 10-15% above average",
                confidence: 0.70,
                provenance: [{ source: "offline_rules", content: "Market timing guidelines" }],
                fallback_used: true
            };
        }

        // Weather advice
        if (questionLower.includes('weather') || questionLower.includes('rain')) {
            return {
                answer: "🌤️ For weather-related decisions:\n• Check local weather forecast\n• Plan field activities around rain\n• Protect crops during extreme weather\n• Use weather apps or radio for updates",
                confidence: 0.65,
                provenance: [{ source: "offline_rules", content: "Weather planning guidelines" }],
                fallback_used: true
            };
        }

        // Default response
        return {
            answer: "🤔 I don't have specific offline guidance for this question. Please:\n• Consult your local agricultural extension officer\n• Visit nearest Krishi Vigyan Kendra\n• Try online mode for AI-powered advice",
            confidence: 0.40,
            provenance: [],
            escalate: true,
            fallback_used: true
        };
    }

    showMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        messageDiv.innerHTML = content;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showBotResponse(response) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        
        let html = `<div>${response.answer}</div>`;
        
        // Add confidence badge
        const confidenceClass = response.confidence >= 0.7 ? 'confidence-high' : 
                               response.confidence >= 0.4 ? 'confidence-medium' : 'confidence-low';
        html += `<div class="confidence-badge ${confidenceClass}">
                    Confidence: ${(response.confidence * 100).toFixed(0)}%
                    ${response.fallback_used ? ' (Offline Rules)' : ''}
                 </div>`;
        
        // Add escalation warning
        if (response.escalate) {
            html += `<div class="escalate-warning">
                        ⚠️ <strong>Expert Consultation Recommended</strong><br>
                        This question requires professional agricultural guidance.
                     </div>`;
        }
        
        // Add provenance (sources)
        if (response.provenance && response.provenance.length > 0) {
            html += '<div class="provenance"><strong>Sources:</strong>';
            response.provenance.slice(0, 2).forEach(source => {
                html += `<div class="provenance-item">
                            <strong>${source.source}</strong>: ${source.content || 'Data source'}
                         </div>`;
            });
            html += '</div>';
        }
        
        messageDiv.innerHTML = html;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    setLoading(isLoading) {
        this.loadingDiv.style.display = isLoading ? 'block' : 'none';
        this.sendButton.disabled = isLoading;
        if (isLoading) {
            this.scrollToBottom();
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AgriSageApp();
});

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
