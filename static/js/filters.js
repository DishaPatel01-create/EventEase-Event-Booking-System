/**
 * EventEasy - Explore Events Interactive Filters & AJAX Search
 */

document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('explore-filters-form');
    const searchInput = document.getElementById('search-query-input');
    const eventsContainer = document.getElementById('events-grid-container');
    const resultsCountEl = document.getElementById('results-count-text');
    const emptyStateEl = document.getElementById('empty-state-container');
    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    const sortSelect = document.getElementById('sort-by-select');

    if (!filterForm || !eventsContainer) return;

    let debounceTimer;

    // Trigger filter update on changes
    function triggerFilter() {
        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData);

        if (sortSelect) {
            params.set('sort', sortSelect.value);
        }
        params.set('format', 'json');

        // Show subtle loading state
        eventsContainer.style.opacity = '0.5';

        fetch(`/events?${params.toString()}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            eventsContainer.style.opacity = '1';
            if (data.success) {
                renderEvents(data.events, data.count);
            }
        })
        .catch(err => {
            console.error('Filter request error:', err);
            eventsContainer.style.opacity = '1';
        });
    }

    // Debounced search on typing
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(triggerFilter, 300);
        });
    }

    // Listen to form inputs change
    filterForm.querySelectorAll('input, select').forEach(input => {
        if (input !== searchInput) {
            input.addEventListener('change', triggerFilter);
        }
    });

    if (sortSelect) {
        sortSelect.addEventListener('change', triggerFilter);
    }

    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', (e) => {
            e.preventDefault();
            filterForm.reset();
            if (searchInput) searchInput.value = '';
            if (sortSelect) sortSelect.value = 'soonest';
            triggerFilter();
        });
    }

    // Render Events in DOM
    function renderEvents(events, count) {
        if (resultsCountEl) {
            resultsCountEl.textContent = `Showing ${count} event${count === 1 ? '' : 's'}`;
        }

        if (count === 0) {
            eventsContainer.innerHTML = '';
            if (emptyStateEl) emptyStateEl.classList.remove('d-none');
            return;
        }

        if (emptyStateEl) emptyStateEl.classList.add('d-none');

        let html = '';
        events.forEach(evt => {
            const isSoldOut = evt.is_sold_out;
            const isLimited = evt.is_limited;
            
            let badgeHtml = '';
            if (evt.category) {
                badgeHtml = `<span class="event-card-badge bg-primary text-white">${evt.category.name}</span>`;
            }

            let availTagHtml = '';
            if (isSoldOut) {
                availTagHtml = `<span class="status-tag sold-out"><i class="fa-solid fa-circle-xmark"></i> Sold Out</span>`;
            } else if (isLimited) {
                availTagHtml = `<span class="status-tag limited"><i class="fa-solid fa-clock"></i> Limited (${evt.total_available} left)</span>`;
            } else {
                availTagHtml = `<span class="status-tag available"><i class="fa-solid fa-check"></i> Available</span>`;
            }

            const priceDisplay = evt.starting_price === 0 ? 'Free' : `₹${Number(evt.starting_price).toLocaleString('en-IN')}`;

            html += `
            <div class="col-md-6 col-lg-4 mb-4 fade-in">
                <div class="event-card">
                    <div class="event-card-img-wrapper">
                        <img src="${evt.image}" alt="${evt.title}" class="event-card-img" loading="lazy">
                        ${badgeHtml}
                    </div>
                    <div class="event-card-body">
                        <div class="event-card-date">
                            <i class="fa-regular fa-calendar text-primary"></i> ${evt.formatted_date}
                        </div>
                        <h5 class="event-card-title">
                            <a href="/events/${evt.id}" class="text-dark">${evt.title}</a>
                        </h5>
                        <div class="event-card-meta">
                            <i class="fa-solid fa-location-dot text-muted"></i> ${evt.venue}, ${evt.city}
                        </div>
                        <div class="mt-2 mb-1">
                            ${availTagHtml}
                        </div>
                    </div>
                    <div class="event-card-footer">
                        <div>
                            <div class="event-card-price-label">Starts from</div>
                            <div class="event-card-price">${priceDisplay}</div>
                        </div>
                        <a href="/events/${evt.id}" class="btn btn-sm btn-primary">
                            View Details <i class="fa-solid fa-arrow-right ms-1"></i>
                        </a>
                    </div>
                </div>
            </div>
            `;
        });

        eventsContainer.innerHTML = html;
    }
});
