document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById('startDetectBtn');
    const videoFeed = document.getElementById('videoFeed');
    const detectionText = document.getElementById('detectionText');
    const confidenceValue = document.getElementById('confidenceValue');
    const confidenceBar = document.getElementById('confidenceBar');

    let detectionInterval = null;

    btn.addEventListener('click', function () {

        videoFeed.src = "/video";

        btn.disabled = true;
        btn.innerHTML = "Detection Running...";

        detectionInterval = setInterval(() => {

            fetch("/detect")   // ✅ ensure this matches app.py
                .then(response => response.json())
                .then(data => {

                    detectionText.textContent = data.name;
                    confidenceValue.textContent = data.confidence + "%";
                    confidenceBar.style.width = data.confidence + "%";

                })
                .catch(error => {
                    console.log("Error fetching result:", error);
                });

        }, 1000);

    });

});