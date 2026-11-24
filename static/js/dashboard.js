/**
 * EventEasy - Dashboard Scripts & Analytics
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Counter Animation for Dashboard Stats
    const counterElements = document.querySelectorAll('.stat-counter');
    counterElements.forEach(counter => {
        const target = parseFloat(counter.getAttribute('data-target')) || 0;
        const prefix = counter.getAttribute('data-prefix') || '';
        const suffix = counter.getAttribute('data-suffix') || '';
        const duration = 1200;
        const stepTime = 20;
        const totalSteps = duration / stepTime;
        let currentStep = 0;

        const timer = setInterval(() => {
            currentStep++;
            const progress = currentStep / totalSteps;
            // Ease out quad
            const easeProgress = 1 - (1 - progress) * (1 - progress);
            const currentVal = target * easeProgress;

            if (target >= 1000) {
                counter.textContent = prefix + Math.floor(currentVal).toLocaleString('en-IN') + suffix;
            } else if (Number.isInteger(target)) {
                counter.textContent = prefix + Math.floor(currentVal) + suffix;
            } else {
                counter.textContent = prefix + currentVal.toFixed(2) + suffix;
            }

            if (currentStep >= totalSteps) {
                clearInterval(timer);
                if (Number.isInteger(target)) {
                    counter.textContent = prefix + target.toLocaleString('en-IN') + suffix;
                } else {
                    counter.textContent = prefix + target.toFixed(2) + suffix;
                }
            }
        }, stepTime);
    });

    // 2. Dynamic Ticket Tier Repeater in Create/Edit Event Form
    const addTicketBtn = document.getElementById('add-ticket-tier-btn');
    const ticketTiersContainer = document.getElementById('ticket-tiers-container');

    if (addTicketBtn && ticketTiersContainer) {
        addTicketBtn.addEventListener('click', () => {
            const index = ticketTiersContainer.querySelectorAll('.ticket-tier-row').length + 1;
            const row = document.createElement('div');
            row.className = 'ticket-tier-row bg-light p-3 rounded-3 mb-3 border position-relative fade-in';
            row.innerHTML = `
                <button type="button" class="btn btn-sm btn-outline-danger position-absolute top-0 end-0 m-2 remove-tier-btn" title="Remove Ticket Tier">
                    <i class="fa-solid fa-trash"></i>
                </button>
                <div class="row g-3">
                    <div class="col-md-5">
                        <label class="form-label small fw-bold">Ticket Tier Name *</label>
                        <input type="text" name="ticket_name[]" class="form-control form-control-sm" placeholder="e.g. VIP Pass, Early Bird" required>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small fw-bold">Price (₹) *</label>
                        <input type="number" step="0.01" min="0" name="ticket_price[]" class="form-control form-control-sm" placeholder="0 for Free" required>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label small fw-bold">Capacity (Total Tickets) *</label>
                        <input type="number" min="1" name="ticket_capacity[]" class="form-control form-control-sm" placeholder="e.g. 100" required>
                    </div>
                    <div class="col-12">
                        <label class="form-label small fw-bold">Description / Perks</label>
                        <input type="text" name="ticket_description[]" class="form-control form-control-sm" placeholder="e.g. Free lunch, front row access">
                    </div>
                </div>
            `;
            ticketTiersContainer.appendChild(row);

            // Bind remove button
            row.querySelector('.remove-tier-btn').addEventListener('click', () => {
                row.remove();
            });
        });

        // Delegate remove existing rows
        ticketTiersContainer.addEventListener('click', (e) => {
            const btn = e.target.closest('.remove-tier-btn');
            if (btn) {
                const row = btn.closest('.ticket-tier-row');
                if (ticketTiersContainer.querySelectorAll('.ticket-tier-row').length > 1) {
                    row.remove();
                } else {
                    alert('You must provide at least one ticket tier for the event.');
                }
            }
        });
    }
});
