// YouTube Success Predictor - Premium Frontend JavaScript

// ===== DOM Elements =====
const titleInput = document.getElementById('title');
const titleLength = document.getElementById('titleLength');
const titleProgress = document.getElementById('titleProgress');
const predictionForm = document.getElementById('predictionForm');
const predictBtn = document.getElementById('predictBtn');
const resultsDiv = document.getElementById('results');
const statsBar = document.getElementById('statsBar');

// ===== Title Character Counter with Progress Bar =====
titleInput.addEventListener('input', function() {
    const length = this.value.length;
    const maxLength = 60;
    const optimalMin = 50;
    const optimalMax = 60;
    
    titleLength.textContent = length;
    
    // Calculate progress percentage
    const progressPercent = Math.min((length / maxLength) * 100, 100);
    titleProgress.style.width = progressPercent + '%';
    
    // Update progress bar color based on optimal range
    titleProgress.classList.remove('optimal', 'warning');
    if (length >= optimalMin && length <= optimalMax) {
        titleProgress.classList.add('optimal');
        titleLength.style.color = '#00D084';
    } else if (length < optimalMin) {
        titleProgress.classList.add('warning');
        titleLength.style.color = '#FFB800';
    } else {
        titleLength.style.color = '#FF4444';
    }
});

// ===== Set Default Publish Date =====
const now = new Date();
now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
document.getElementById('publish_date').value = now.toISOString().slice(0, 16);

// ===== Animated Number Counter =====
function animateNumber(element, target, duration = 1000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = formatNumber(Math.floor(current));
    }, 16);
}

// ===== Format Number with Turkish Locale =====
function formatNumber(num) {
    return new Intl.NumberFormat('tr-TR').format(Math.floor(num));
}

// ===== Form Submission =====
predictionForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Collect form data
    const formData = new FormData(this);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        if (key === 'publish_date') {
            const date = new Date(value);
            data[key] = date.toISOString();
        } else if (key === 'duration_minutes' || key === 'tag_count' || 
                   key === 'channel_subscribers' || key === 'channel_video_count') {
            data[key] = parseFloat(value) || 0;
        } else if (key === 'publish_hour') {
            data[key] = parseInt(value);
        } else {
            data[key] = value;
        }
    }
    
    // Show loading state
    showLoadingState();
    
    // Hide previous results/errors
    hideResults();
    hideError();
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Small delay for better UX
            await new Promise(resolve => setTimeout(resolve, 500));
            displayResults(result);
        } else {
            displayError(result.error || 'Bir hata oluştu');
        }
    } catch (error) {
        displayError('Sunucuya bağlanılamadı. Lütfen tekrar deneyin.');
        console.error('Error:', error);
    } finally {
        hideLoadingState();
    }
});

// ===== Loading State =====
function showLoadingState() {
    const btnText = predictBtn.querySelector('.btn-text');
    const btnLoading = predictBtn.querySelector('.btn-loading');
    
    predictBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'flex';
}

function hideLoadingState() {
    const btnText = predictBtn.querySelector('.btn-text');
    const btnLoading = predictBtn.querySelector('.btn-loading');
    
    predictBtn.disabled = false;
    btnText.style.display = 'flex';
    btnLoading.style.display = 'none';
}

// ===== Display Results =====
function displayResults(result) {
    const prediction = result.prediction;
    
    // Show stats bar
    statsBar.style.display = 'grid';
    animateNumber(document.getElementById('predictionStat'), prediction.first_week_views);
    
    // Update confidence with accuracy if available
    const confidencePercent = (prediction.confidence * 100).toFixed(0);
    const accuracyPercent = prediction.accuracy ? prediction.accuracy.toFixed(0) : confidencePercent;
    document.getElementById('confidenceStat').textContent = accuracyPercent + '%';
    document.getElementById('featuresStat').textContent = result.features_used + '+';
    
    // Update prediction value with animation
    const predictionValueEl = document.getElementById('predictionValue');
    animateNumber(predictionValueEl, prediction.first_week_views, 1500);
    
    // Update prediction range (tighter intervals)
    const minViews = prediction.range.min;
    const maxViews = prediction.range.max;
    const expectedViews = prediction.first_week_views;
    const margin = prediction.margin || Math.round((maxViews - minViews) / 2);
    
    document.getElementById('predictionRange').textContent = 
        `${formatNumber(minViews)} - ${formatNumber(maxViews)} görüntülenme (±${formatNumber(margin)})`;
    
    // Update metrics with animation
    setTimeout(() => {
        animateNumber(document.getElementById('minViews'), minViews);
        animateNumber(document.getElementById('expectedViews'), expectedViews);
        animateNumber(document.getElementById('maxViews'), maxViews);
    }, 300);
    
    // Update confidence badge with accuracy
    const confidenceBadge = document.getElementById('confidenceBadge');
    confidenceBadge.className = 'confidence-badge';
    const displayConfidence = Math.max(parseFloat(confidencePercent), parseFloat(accuracyPercent));
    
    if (displayConfidence >= 85) {
        confidenceBadge.style.background = 'linear-gradient(135deg, #00D084 0%, #00A869 100%)';
        document.getElementById('confidenceText').textContent = displayConfidence + '% Accuracy';
    } else if (displayConfidence >= 75) {
        confidenceBadge.style.background = 'linear-gradient(135deg, #3EA6FF 0%, #1E88E5 100%)';
        document.getElementById('confidenceText').textContent = displayConfidence + '% Accuracy';
    } else if (displayConfidence >= 70) {
        confidenceBadge.style.background = 'linear-gradient(135deg, #FFB800 0%, #FF9800 100%)';
        document.getElementById('confidenceText').textContent = displayConfidence + '% Accuracy';
    } else {
        confidenceBadge.style.background = 'linear-gradient(135deg, #FF4444 0%, #CC0000 100%)';
        document.getElementById('confidenceText').textContent = displayConfidence + '% Accuracy';
    }
    
    // Update prediction chart
    updatePredictionChart(minViews, expectedViews, maxViews);
    
    // Display recommendations
    displayRecommendations(result.recommendations || []);
    
    // Update model info
    if (result.model_info) {
        if (result.model_info.model_name) {
            const modelNameEl = document.getElementById('modelName');
            if (modelNameEl) {
                modelNameEl.textContent = `Powered by ${result.model_info.model_name}`;
            }
        }
    }
    
    if (result.features_used) {
        const featureCountEl = document.getElementById('featureCount');
        if (featureCountEl) {
            featureCountEl.textContent = `${result.features_used}+ Features Analyzed`;
        }
    }
    
    if (prediction.accuracy) {
        const modelAccuracyEl = document.getElementById('modelAccuracy');
        if (modelAccuracyEl) {
            modelAccuracyEl.textContent = `${prediction.accuracy.toFixed(0)}% Prediction Accuracy`;
        }
    }
    
    // Show results with animation
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Add fade-in animation
    resultsDiv.style.animation = 'fadeInUp 0.8s ease-out';
}

// ===== Update Prediction Chart =====
function updatePredictionChart(min, expected, max) {
    const chartFill = document.getElementById('chartFill');
    // Calculate percentage based on expected value relative to max
    const percentage = (expected / max) * 100;
    
    // Animate chart fill
    setTimeout(() => {
        chartFill.style.width = percentage + '%';
    }, 500);
}

// ===== Display Recommendations =====
function displayRecommendations(recommendations) {
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    
    if (recommendations.length === 0) {
        recommendationsList.innerHTML = `
            <div class="recommendation-item" style="border-left-color: #00D084;">
                <div class="recommendation-priority low">Mükemmel!</div>
                <div class="recommendation-message">Videonuz optimal ayarlara sahip görünüyor. Harika iş!</div>
                <div class="recommendation-suggestion">🎉 Tüm öneriler uygulanmış durumda.</div>
            </div>
        `;
        return;
    }
    
    recommendations.forEach((rec, index) => {
        setTimeout(() => {
            const recItem = document.createElement('div');
            recItem.className = `recommendation-item ${rec.priority}`;
            
            const priorityText = {
                'high': 'Yüksek Öncelik',
                'medium': 'Orta Öncelik',
                'low': 'Düşük Öncelik'
            };
            
            recItem.innerHTML = `
                <div class="recommendation-priority ${rec.priority}">
                    ${priorityText[rec.priority] || 'Öneri'}
                </div>
                <div class="recommendation-message">${rec.message}</div>
                <div class="recommendation-suggestion">💡 ${rec.suggestion}</div>
            `;
            
            recommendationsList.appendChild(recItem);
        }, index * 100);
    });
}

// ===== Display Error =====
function displayError(message) {
    const errorDiv = document.getElementById('error');
    document.getElementById('errorMessage').textContent = message;
    errorDiv.style.display = 'block';
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ===== Hide Results =====
function hideResults() {
    resultsDiv.style.display = 'none';
    statsBar.style.display = 'none';
}

// ===== Hide Error =====
function hideError() {
    document.getElementById('error').style.display = 'none';
}

// ===== Check API Health on Load =====
window.addEventListener('load', async function() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (!data.model_loaded) {
            console.warn('Model not loaded. Please train the model first.');
            // Show warning in UI
            const headerBadge = document.querySelector('.header-badge');
            if (headerBadge) {
                headerBadge.innerHTML = '<span class="badge-dot" style="background: #FF4444;"></span><span>Model Not Loaded</span>';
                headerBadge.style.background = 'rgba(255, 68, 68, 0.1)';
                headerBadge.style.borderColor = 'rgba(255, 68, 68, 0.3)';
                headerBadge.style.color = '#FF4444';
            }
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
});

// ===== Add Smooth Scrolling =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ===== Add Input Animations =====
document.querySelectorAll('.form-input, .form-textarea, .form-select').forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement.style.transform = 'scale(1.02)';
    });
    
    input.addEventListener('blur', function() {
        this.parentElement.style.transform = 'scale(1)';
    });
});

// ===== Intersection Observer for Animations =====
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all cards
document.querySelectorAll('.glass-card, .stat-item, .metric-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(card);
});

// ===== Add Hover Effects =====
document.querySelectorAll('.form-input, .form-textarea, .form-select').forEach(input => {
    input.addEventListener('mouseenter', function() {
        this.style.borderColor = 'rgba(62, 166, 255, 0.5)';
    });
    
    input.addEventListener('mouseleave', function() {
        if (document.activeElement !== this) {
            this.style.borderColor = '';
        }
    });
});

// ===== Performance Optimization =====
// Debounce function for expensive operations
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Debounced title input handler
const debouncedTitleUpdate = debounce(() => {
    // Additional processing if needed
}, 300);

titleInput.addEventListener('input', debouncedTitleUpdate);

// ===== Console Welcome Message =====
console.log('%c🎬 YouTube Success Predictor', 'font-size: 20px; font-weight: bold; color: #FF0000;');
console.log('%cAI-Powered Video Performance Analytics', 'font-size: 12px; color: #B0B0B0;');
console.log('%cBuilt with Machine Learning • XGBoost • Flask', 'font-size: 10px; color: #707070;');
