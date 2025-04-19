let reviewId = "";

document.getElementById('reviewForm').addEventListener('submit', async function(event) {
  event.preventDefault();

  const domain = document.getElementById('domainInput').value.trim();
  const loader = document.getElementById('loader');
  const reviewResult = document.getElementById('reviewResult');

  if (!domain) {
    alert('Please enter your portfolio site domain');
    return;
  }

  loader.style.display = "block";

  try {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    const response = await fetch('submit-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ domain })
    });

    if (!response.ok) {
      const errorText = await response.text();
      alert(`Server Error (${response.status}): ${errorText}`);
      return;
    }

    const data = await response.json();

    const formattedReview = data.website_review;

    reviewResult.innerHTML = `
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h3 class="text-lg font-bold">Portfolio Feedback:</h3>
          <div class="w-full p-2 border border-gray-300 bg-white rounded whitespace-pre-wrap" style="height: calc(100% - 1rem); overflow-y: auto;">${formattedReview}</div>
        </div>
        <div class="flex justify-center md:justify-end">
          <div class="w-full max-w-md">
            <h3 class="text-lg font-bold">Screenshot:</h3>
            <img src="${data.website_screenshot}" alt="Website Screenshot" class="mt-2 w-full h-auto" />
          </div>
        </div>
      </div>
    `;

    reviewId = data.review_id;
    reviewResult.classList.remove('hidden');

  } catch (error) {
    console.error('Error submitting form:', error);
    alert("An unexpected error occurred. Please try again later.");
  } finally {
    loader.style.display = "none";
  }
});
