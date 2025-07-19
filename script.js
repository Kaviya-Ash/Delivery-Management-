// Toggle product descriptions
document.querySelectorAll('.product-btn').forEach(button => {
    button.addEventListener('click', () => {
        const targetId = button.getAttribute('data-target');
        const description = document.getElementById(targetId);
        description.classList.toggle('hidden');
    });
});

// Calculate Total Price
function calculateTotal() {
    let total = 0;
    const prices = {
        "bio-small": 25, "bio-medium": 45, "bio-large": 75,
        "paper-small": 10, "paper-medium": 15, "paper-large": 20,
        "container-small": 30, "container-medium": 50, "container-large": 80,
        "recycled-small": 15, "recycled-medium": 25, "recycled-large": 35
    };

    for (let key in prices) {
        const qty = parseInt(document.getElementById(key).value) || 0;
        if (qty < 0) {
            alert("Quantity cannot be negative.");
            return;
        }
        total += qty * prices[key];
    }

    document.getElementById("totalPrice").textContent = total;
}

// Payment Mode Handling
document.querySelectorAll('input[name="payment"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        if (e.target.value === 'online') {
            document.getElementById('qrModal').style.display = 'flex';
        }
    });
});

function closeQRModal() {
    document.getElementById('qrModal').style.display = 'none';
}

// Handle Order Form Submission
document.getElementById("orderForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const total = document.getElementById('totalPrice').textContent;
    if (total === '0') {
        alert("Please add items to your order before submitting");
        return;
    }
    alert(`Order placed successfully!\nTotal Amount: ₹${total}`);
    this.reset();
    document.getElementById('totalPrice').textContent = '0';
});

// Handle Reviews
document.getElementById("reviewForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const comment = document.getElementById("comment").value;
    const rating = document.getElementById("rating").value;
    
    const review = document.createElement("div");
    review.innerHTML = `<strong>Rating: ${'★'.repeat(rating)}</strong><br>${comment}`;
    document.getElementById("reviewsContainer").prepend(review);
    
    this.reset();
});

// Initialize descriptions as hidden on page load
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.description').forEach(desc => {
        desc.classList.add('hidden');
    });
});