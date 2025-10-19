// Dynamic Pricing Plans Loader
async function loadPricingPlans() {
    try {
        const response = await fetch('/get_payment_plans');
        const data = await response.json();
        
        if (data.error) {
            console.error('Error loading pricing plans:', data.error);
            return;
        }
        
        // Clear existing pricing grid
        const pricingGrid = document.querySelector('.pricing-grid');
        if (!pricingGrid) return;
        
        pricingGrid.innerHTML = '';
        
        // Generate pricing cards
        data.plans.forEach(plan => {
            const cardHTML = generatePricingCard(plan);
            pricingGrid.insertAdjacentHTML('beforeend', cardHTML);
        });
        
        // Update pricing note
        updatePricingNote(data.conversion);
        
    } catch (error) {
        console.error('Error loading pricing plans:', error);
    }
}

function generatePricingCard(plan) {
    const featuredClass = plan.is_featured ? 'featured' : '';
    const savingsHTML = plan.savings ? `<div class="savings">${plan.savings}</div>` : '';
    
    const featuresHTML = plan.features.map(feature => `<li>${feature}</li>`).join('');
    
    return `
        <div class="pricing-card autoShow ${featuredClass}">
            <div class="pricing-header">
                <h3>${plan.plan_name}</h3>
                <div class="pricing-badge ${plan.badge === 'Best Value' ? 'best-value' : ''}">${plan.badge}</div>
            </div>
            <div class="pricing-price">
                <span class="currency">₹</span>
                <span class="amount">${plan.amount}</span>
                <span class="period">${plan.id === 'starter' ? '/one-time' : plan.id === 'monthly' ? '/month' : '/3 months'}</span>
            </div>
            <div class="pricing-credits">
                <span class="credits-number">${plan.credits}</span>
                <span class="credits-text">Credits</span>
            </div>
            ${savingsHTML}
            <ul class="pricing-features">
                ${featuresHTML}
            </ul>
            <button class="pricing-button ${plan.button_class}" onclick="initiatePayment('${plan.id}')">
                <span>${plan.button_text}</span>
            </button>
        </div>
    `;
}

function updatePricingNote(conversion) {
    const pricingNote = document.querySelector('.pricing-note p');
    if (pricingNote) {
        pricingNote.innerHTML = `💡 <strong>Pro Tip:</strong> ${conversion.rule}. ${conversion.description}. Perfect for last-minute submissions and exam prep! Choose the plan that fits your semester workload.`;
    }
}

// Load pricing plans when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Only load if we're on a page with pricing section
    if (document.querySelector('.pricing-section')) {
        loadPricingPlans();
    }
});

// Export for use in other scripts
window.loadPricingPlans = loadPricingPlans;
