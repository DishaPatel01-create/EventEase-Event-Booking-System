/**
 * EventEasy - Booking and Checkout Interactive Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. EVENT DETAILS - TICKET SELECTION & LIVE PRICE CALCULATOR
    const ticketSteppers = document.querySelectorAll('.ticket-quantity-stepper');
    const bookNowBtn = document.getElementById('proceed-to-checkout-btn');
    const liveSubtotalEl = document.getElementById('live-booking-subtotal');
    const liveTicketCountEl = document.getElementById('live-ticket-count');

    function updateLiveSummary() {
        let totalCount = 0;
        let totalPrice = 0;
        const selectedTickets = {};

        ticketSteppers.forEach(stepper => {
            const input = stepper.querySelector('input[type="number"]');
            const qty = parseInt(input.value) || 0;
            const price = parseFloat(input.dataset.price) || 0;
            const ticketId = input.dataset.ticketId;

            if (qty > 0) {
                totalCount += qty;
                totalPrice += (qty * price);
                selectedTickets[ticketId] = qty;
            }
        });

        if (liveTicketCountEl) liveTicketCountEl.textContent = totalCount;
        if (liveSubtotalEl) {
            liveSubtotalEl.textContent = totalPrice === 0 ? '₹0' : '₹' + totalPrice.toLocaleString('en-IN');
        }

        if (bookNowBtn) {
            if (totalCount > 0) {
                bookNowBtn.removeAttribute('disabled');
                bookNowBtn.classList.remove('opacity-50');
            } else {
                bookNowBtn.setAttribute('disabled', 'true');
                bookNowBtn.classList.add('opacity-50');
            }
        }

        // Store selection in hidden checkout form if present
        const ticketsJsonInput = document.getElementById('tickets-json-input');
        if (ticketsJsonInput) {
            ticketsJsonInput.value = JSON.stringify(selectedTickets);
        }
    }

    ticketSteppers.forEach(stepper => {
        const minusBtn = stepper.querySelector('.btn-qty-minus');
        const plusBtn = stepper.querySelector('.btn-qty-plus');
        const input = stepper.querySelector('input[type="number"]');
        const maxQty = parseInt(input.getAttribute('max')) || 10;

        if (minusBtn && plusBtn && input) {
            minusBtn.addEventListener('click', () => {
                let current = parseInt(input.value) || 0;
                if (current > 0) {
                    input.value = current - 1;
                    updateLiveSummary();
                }
            });

            plusBtn.addEventListener('click', () => {
                let current = parseInt(input.value) || 0;
                if (current < maxQty && current < 10) { // Max 10 per transaction
                    input.value = current + 1;
                    updateLiveSummary();
                } else if (current >= maxQty) {
                    alert(`Only ${maxQty} tickets available for this tier.`);
                }
            });

            input.addEventListener('change', () => {
                let val = parseInt(input.value) || 0;
                if (val < 0) val = 0;
                if (val > maxQty) val = maxQty;
                input.value = val;
                updateLiveSummary();
            });
        }
    });

    // 2. CHECKOUT PAGE - SIMULATED PAYMENT METHOD SELECTOR & SUBMISSION
    const paymentCards = document.querySelectorAll('.payment-method-card');
    const paymentMethodInput = document.getElementById('selected-payment-method');
    const paymentForm = document.getElementById('checkout-payment-form');
    const paySubmitBtn = document.getElementById('pay-and-confirm-btn');
    const paymentSpinner = document.getElementById('payment-processing-spinner');
    const paymentBtnText = document.getElementById('payment-btn-text');

    paymentCards.forEach(card => {
        card.addEventListener('click', () => {
            paymentCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            const method = card.dataset.method;
            if (paymentMethodInput) paymentMethodInput.value = method;

            // Toggle specific payment sub-forms (UPI vs Card vs NetBanking)
            document.querySelectorAll('.payment-subform').forEach(sf => sf.classList.add('d-none'));
            const targetSubform = document.getElementById(`subform-${method.toLowerCase().replace(/[^a-z]/g, '')}`);
            if (targetSubform) targetSubform.classList.remove('d-none');
        });
    });

    if (paymentForm && paySubmitBtn) {
        paymentForm.addEventListener('submit', (e) => {
            e.preventDefault();

            // Disable button and show simulated processing animation
            paySubmitBtn.setAttribute('disabled', 'true');
            if (paymentSpinner) paymentSpinner.classList.remove('d-none');
            if (paymentBtnText) paymentBtnText.textContent = 'Processing Payment Securely...';

            const formData = new FormData(paymentForm);
            const dataObj = {};
            formData.forEach((value, key) => dataObj[key] = value);

            // Realistic simulated delay of 1.5 seconds to feel like a real banking gateway
            setTimeout(() => {
                fetch('/checkout/process', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(dataObj)
                })
                .then(res => res.json())
                .then(resData => {
                    if (resData.success) {
                        window.location.href = resData.redirect_url;
                    } else {
                        alert(resData.message || 'Payment could not be processed.');
                        paySubmitBtn.removeAttribute('disabled');
                        if (paymentSpinner) paymentSpinner.classList.add('d-none');
                        if (paymentBtnText) paymentBtnText.textContent = 'Pay & Confirm Booking';
                    }
                })
                .catch(err => {
                    console.error('Payment error:', err);
                    alert('Network error occurred during payment processing. Please try again.');
                    paySubmitBtn.removeAttribute('disabled');
                    if (paymentSpinner) paymentSpinner.classList.add('d-none');
                    if (paymentBtnText) paymentBtnText.textContent = 'Pay & Confirm Booking';
                });
            }, 1400);
        });
    }
});
