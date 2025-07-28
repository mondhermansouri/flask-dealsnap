// DealSnap App JavaScript

// PWA Installation
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    
    // Show install button/banner
    showInstallBanner();
});

function showInstallBanner() {
    // Create install banner if it doesn't exist
    if (!document.getElementById('install-banner')) {
        const banner = document.createElement('div');
        banner.id = 'install-banner';
        banner.className = 'alert alert-info alert-dismissible fade show position-fixed bottom-0 start-0 end-0 m-3';
        banner.style.zIndex = '1050';
        banner.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas fa-mobile-alt me-2"></i>
                    <strong>Install DealSnap</strong> - Get quick access to the best deals!
                </div>
                <div>
                    <button class="btn btn-sm btn-primary me-2" onclick="installPWA()">Install</button>
                    <button class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            </div>
        `;
        document.body.appendChild(banner);
    }
}

function installPWA() {
    if (deferredPrompt) {
        // Show the prompt
        deferredPrompt.prompt();
        
        // Wait for the user to respond to the prompt
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
                // Hide install banner
                const banner = document.getElementById('install-banner');
                if (banner) banner.remove();
            }
            deferredPrompt = null;
        });
    }
}

// Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Deal Analytics
function trackDealView(dealId) {
    // Track deal view for analytics
    fetch(`/api/deal/${dealId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    }).catch(error => {
        console.error('Error tracking view:', error);
    });
}

// Lazy Loading for Images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});

// Share API Support
function shareDeal(title, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: 'Check out this amazing deal on DealSnap!',
            url: url
        }).catch(console.error);
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(url).then(() => {
            showToast('Deal link copied to clipboard!');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = url;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showToast('Deal link copied!');
        });
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    const toastContainer = getOrCreateToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
    }
    return container;
}

// Category Filter with URL Update
function filterByCategory(category) {
    const url = new URL(window.location);
    if (category === 'all') {
        url.searchParams.delete('category');
    } else {
        url.searchParams.set('category', category);
    }
    window.location.href = url.toString();
}

// Infinite Scroll (for future enhancement)
function initInfiniteScroll() {
    let loading = false;
    let page = 1;
    
    window.addEventListener('scroll', () => {
        if (loading) return;
        
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
            loading = true;
            loadMoreDeals(page + 1).then(() => {
                page++;
                loading = false;
            });
        }
    });
}

async function loadMoreDeals(page) {
    try {
        const response = await fetch(`/api/deals?page=${page}&limit=12`);
        const data = await response.json();
        
        if (data.deals && data.deals.length > 0) {
            // Append new deals to the grid
            appendDealsToGrid(data.deals);
        }
    } catch (error) {
        console.error('Error loading more deals:', error);
    }
}

function appendDealsToGrid(deals) {
    const grid = document.querySelector('.deals-grid');
    if (!grid) return;
    
    deals.forEach(deal => {
        const dealCard = createDealCard(deal);
        grid.appendChild(dealCard);
    });
}

function createDealCard(deal) {
    const card = document.createElement('div');
    card.className = 'col-lg-4 col-md-6 col-sm-12 mb-4';
    card.innerHTML = `
        <div class="card deal-card h-100">
            ${deal.image_url ? 
                `<img src="${deal.image_url}" class="card-img-top deal-image" alt="${deal.title}">` :
                `<div class="placeholder-image card-img-top d-flex align-items-center justify-content-center">
                    <i class="fas fa-image fa-2x text-muted"></i>
                </div>`
            }
            <div class="card-body d-flex flex-column">
                <h6 class="card-title">${deal.ai_headline || deal.title}</h6>
                <p class="card-text flex-grow-1">${deal.description.substring(0, 80)}...</p>
                <div class="price-section mb-3">
                    <span class="current-price">$${deal.price.toFixed(2)}</span>
                    ${deal.original_price && deal.original_price > deal.price ? 
                        `<span class="original-price">$${deal.original_price.toFixed(2)}</span>
                         <span class="discount-badge">${deal.discount_percentage}% OFF</span>` : ''
                    }
                </div>
                <div class="d-flex gap-2">
                    <a href="/deal/${deal.id}" class="btn btn-outline-primary btn-sm flex-grow-1">
                        <i class="fas fa-info-circle me-1"></i>Details
                    </a>
                    <a href="/click/${deal.id}" class="btn btn-warning btn-sm flex-grow-1">
                        <i class="fas fa-shopping-cart me-1"></i>Get Deal
                    </a>
                </div>
            </div>
        </div>
    `;
    return card;
}

// Performance Monitoring
function trackPerformance() {
    if ('performance' in window) {
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page Load Time:', perfData.loadEventEnd - perfData.loadEventStart);
        });
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    trackPerformance();
    
    // Add click tracking to deal links
    document.querySelectorAll('a[href*="/click/"]').forEach(link => {
        link.addEventListener('click', function() {
            // Track click event
            const dealId = this.href.split('/click/')[1];
            console.log('Deal clicked:', dealId);
        });
    });
});

// Error Handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // Could send to analytics service
});

// Network Status
window.addEventListener('online', () => {
    showToast('You are back online!', 'success');
});

window.addEventListener('offline', () => {
    showToast('You are currently offline. Some features may not work.', 'warning');
});
