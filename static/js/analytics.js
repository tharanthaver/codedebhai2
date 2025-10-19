// Google Analytics Custom Event Tracking for CodeDeBhai
// This file tracks important user interactions for better analytics

// Track PDF uploads
function trackPdfUpload(language, hasTemplate) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'pdf_upload', {
            'event_category': 'engagement',
            'event_label': language,
            'custom_parameters': {
                'programming_language': language,
                'has_template': hasTemplate ? 'yes' : 'no'
            }
        });
    }
}

// Track manual question submissions
function trackManualQuestions(questionCount, language) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'manual_questions', {
            'event_category': 'engagement',
            'event_label': language,
            'value': questionCount,
            'custom_parameters': {
                'question_count': questionCount,
                'programming_language': language
            }
        });
    }
}

// Track user login/signup
function trackUserAuthentication(action, method) {
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            'event_category': 'user_authentication',
            'event_label': method,
            'custom_parameters': {
                'auth_method': method
            }
        });
    }
}

// Track payment attempts
function trackPaymentAttempt(planType, amount) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'begin_checkout', {
            'event_category': 'ecommerce',
            'currency': 'INR',
            'value': amount,
            'items': [{
                'item_id': planType,
                'item_name': planType + '_plan',
                'category': 'credits',
                'quantity': 1,
                'price': amount
            }]
        });
    }
}

// Track successful payments
function trackPaymentSuccess(planType, amount, orderId) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'purchase', {
            'event_category': 'ecommerce',
            'transaction_id': orderId,
            'currency': 'INR',
            'value': amount,
            'items': [{
                'item_id': planType,
                'item_name': planType + '_plan',
                'category': 'credits',
                'quantity': 1,
                'price': amount
            }]
        });
    }
}

// Track failed payments
function trackPaymentFailure(planType, amount, reason) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'payment_failed', {
            'event_category': 'ecommerce',
            'event_label': reason,
            'value': amount,
            'custom_parameters': {
                'plan_type': planType,
                'failure_reason': reason
            }
        });
    }
}

// Track file downloads
function trackFileDownload(fileType, processingTime) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'file_download', {
            'event_category': 'engagement',
            'event_label': fileType,
            'value': Math.round(processingTime),
            'custom_parameters': {
                'file_type': fileType,
                'processing_time_seconds': processingTime
            }
        });
    }
}

// Track template usage
function trackTemplateUsage(templateType) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'template_usage', {
            'event_category': 'features',
            'event_label': templateType,
            'custom_parameters': {
                'template_type': templateType
            }
        });
    }
}

// Track customization usage
function trackCustomizationUsage() {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'customization_used', {
            'event_category': 'features',
            'event_label': 'document_styling'
        });
    }
}

// Track page scroll depth (to understand user engagement)
function trackScrollDepth() {
    if (typeof gtag === 'undefined') return;
    
    let maxScroll = 0;
    const milestones = [25, 50, 75, 90];
    let trackedMilestones = [];
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.body.offsetHeight;
        const winHeight = window.innerHeight;
        const scrollPercent = Math.round((scrollTop / (docHeight - winHeight)) * 100);
        
        if (scrollPercent > maxScroll) {
            maxScroll = scrollPercent;
            
            milestones.forEach(milestone => {
                if (scrollPercent >= milestone && !trackedMilestones.includes(milestone)) {
                    trackedMilestones.push(milestone);
                    gtag('event', 'scroll_depth', {
                        'event_category': 'engagement',
                        'event_label': milestone + '%',
                        'value': milestone
                    });
                }
            });
        }
    });
}

// Track form interactions
function trackFormInteraction(formType, action) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'form_interaction', {
            'event_category': 'engagement',
            'event_label': formType + '_' + action,
            'custom_parameters': {
                'form_type': formType,
                'interaction': action
            }
        });
    }
}

// Track error events
function trackError(errorType, errorMessage) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'exception', {
            'description': errorType + ': ' + errorMessage,
            'fatal': false,
            'custom_parameters': {
                'error_type': errorType,
                'error_message': errorMessage
            }
        });
    }
}

// Track button clicks
function trackButtonClick(buttonName, location) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'button_click', {
            'event_category': 'engagement',
            'event_label': buttonName,
            'custom_parameters': {
                'button_name': buttonName,
                'page_location': location
            }
        });
    }
}

// Track modal interactions
function trackModalInteraction(modalName, action) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'modal_interaction', {
            'event_category': 'engagement',
            'event_label': modalName + '_' + action,
            'custom_parameters': {
                'modal_name': modalName,
                'action': action
            }
        });
    }
}

// Initialize tracking when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Track scroll depth
    trackScrollDepth();
    
    // Track time on page
    const startTime = Date.now();
    window.addEventListener('beforeunload', function() {
        const timeOnPage = Math.round((Date.now() - startTime) / 1000);
        if (typeof gtag !== 'undefined') {
            gtag('event', 'time_on_page', {
                'event_category': 'engagement',
                'value': timeOnPage,
                'custom_parameters': {
                    'seconds_on_page': timeOnPage
                }
            });
        }
    });
});

// Export functions for global use
window.analyticsTracker = {
    trackPdfUpload,
    trackManualQuestions,
    trackUserAuthentication,
    trackPaymentAttempt,
    trackPaymentSuccess,
    trackPaymentFailure,
    trackFileDownload,
    trackTemplateUsage,
    trackCustomizationUsage,
    trackFormInteraction,
    trackError,
    trackButtonClick,
    trackModalInteraction
};
