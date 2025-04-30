// --- PWA Service Worker Registration ---
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registration successful with scope: ', registration.scope);
      })
      .catch(error => {
        console.log('ServiceWorker registration failed: ', error);
      });
  });
}

// --- Form Handling ---
const form = document.getElementById('explain-form');
const submitButton = document.getElementById('submit-button');
const outputDiv = document.getElementById('explanation-output');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error-message');

form.addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent default form submission

    // Get form data
    const abilities = document.getElementById('abilities').value.trim();
    const likes = document.getElementById('likes').value.trim();
    const topic = document.getElementById('topic').value.trim();
    const language = document.getElementById('language').value;

    if (!topic) {
        showError("Please enter a topic you want to learn about.");
        return;
    }

    // Show loading state and disable button
    showLoading(true);
    hideError();
    outputDiv.innerHTML = '<p>Your tailored explanation will appear here.</p>'; // Clear previous output

    try {
        const response = await fetch('/explain', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                abilities: abilities,
                likes: likes,
                topic: topic,
                language: language
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            // Handle HTTP errors (like 4xx, 5xx)
            throw new Error(data.error || `Server error: ${response.status}`);
        }

        if (data.error) {
             // Handle errors reported by the backend logic
            throw new Error(data.error);
        }

        // Display the explanation (using innerHTML as Gemini might return Markdown/HTML)
        // Basic sanitization could be added here if needed, but we trust the Gemini source for now.
        outputDiv.innerHTML = data.explanation || "<p>No explanation received.</p>";

    } catch (error) {
        console.error('Error fetching explanation:', error);
        showError(`Failed to get explanation: ${error.message}`);
        outputDiv.innerHTML = '<p>Could not fetch explanation. Please try again.</p>'; // Clear output on error
    } finally {
        // Hide loading state and re-enable button
        showLoading(false);
    }
});

// --- Helper Functions ---
function showLoading(isLoading) {
    if (isLoading) {
        loadingDiv.classList.remove('hidden');
        submitButton.disabled = true;
        submitButton.textContent = 'Thinking...';
    } else {
        loadingDiv.classList.add('hidden');
        submitButton.disabled = false;
        submitButton.textContent = 'Explain It!';
    }
}

function showError(message) {
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    errorDiv.classList.add('hidden');
    errorDiv.textContent = '';
}