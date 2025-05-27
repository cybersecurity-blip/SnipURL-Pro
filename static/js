// DOM Elements
const shortenForm = document.getElementById('shortenForm');
const resultContainer = document.getElementById('resultContainer');
const shortUrlInput = document.getElementById('shortUrl');
const copyBtn = document.getElementById('copyBtn');
const loginBtn = document.getElementById('loginBtn');
const analyticsLink = document.getElementById('analyticsLink');

// Google Login
function handleCredentialResponse(response) {
    console.log("Google Login Response:", response);
    // Send to your backend for verification
    fetch('/api/auth/google', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ credential: response.credential })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Login success:", data);
        // Update UI for logged in user
        loginBtn.textContent = "Dashboard";
        loginBtn.href = "/dashboard";
    })
    .catch(error => {
        console.error("Login error:", error);
    });
}

// Initialize Google Sign-In
window.onload = function() {
    google.accounts.id.initialize({
        client_id: "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com",
        callback: handleCredentialResponse
    });
    
    google.accounts.id.renderButton(
        document.getElementById("googleLoginBtn"),
        { theme: "outline", size: "medium" }
    );
};

// URL Shortening
shortenForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const longUrl = shortenForm.querySelector('input').value;
    
    try {
        const response = await fetch('/api/shorten', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: longUrl })
        });
        
        const data = await response.json();
        
        if (data.shortUrl) {
            shortUrlInput.value = data.shortUrl;
            resultContainer.style.display = 'block';
            
            // Set expiration date (14 days from now)
            const expires = new Date();
            expires.setDate(expires.getDate() + 14);
            document.getElementById('linkExpiry').textContent = `Expires on ${expires.toLocaleDateString()}`;
            
            // Load ads after result is shown
            (adsbygoogle = window.adsbygoogle || []).push({});
        } else {
            alert(data.error || "Failed to shorten URL");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    }
});

// Copy to Clipboard
copyBtn.addEventListener('click', () => {
    shortUrlInput.select();
    document.execCommand('copy');
    
    // Visual feedback
    const originalText = copyBtn.innerHTML;
    copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
    setTimeout(() => {
        copyBtn.innerHTML = originalText;
    }, 2000);
});

// Initialize Google Ads
window.addEventListener('load', () => {
    // Load top ad
    (adsbygoogle = window.adsbygoogle || []).push({});
    
    // Track link clicks if coming from a short URL
    if (window.location.search.includes('?ref=')) {
        const shortCode = window.location.search.split('?ref=')[1];
        fetch(`/api/track/${shortCode}`);
    }
});
