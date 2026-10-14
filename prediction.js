document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("predictionForm");
    const result = document.getElementById("predictionResult");
    const button = document.getElementById("predictButton");

    // Check whether all required HTML elements exist
    if (!form || !result || !button) {
        console.error("Prediction page elements not found.");
        return;
    }

    // Display messages and prediction results
    function showMessage(message, className = "") {
        result.style.display = "block";
        result.className = className;
        result.textContent = message;
    }

    // Handle prediction form submission
    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const averageField = document.getElementById("averageTCI");
        const maxField = document.getElementById("maxTCI");

        if (!averageField || !maxField) {
            showMessage(
                "Error: Check the input IDs in predict.html.",
                "result-error"
            );
            return;
        }

        // Read input values
        const averageText = averageField.value.trim();
        const maxText = maxField.value.trim();

        if (averageText === "" || maxText === "") {
            showMessage(
                "Please enter both Average TCI and Maximum TCI.",
                "result-error"
            );
            return;
        }

        const averageTCI = Number(averageText);
        const maxTCI = Number(maxText);

        // Validate the inputs
        if (
            !Number.isFinite(averageTCI) ||
            !Number.isFinite(maxTCI) ||
            averageTCI < 0 ||
            maxTCI < 0
        ) {
            showMessage(
                "Please enter valid, non-negative TCI values.",
                "result-error"
            );
            return;
        }

        if (averageTCI > maxTCI) {
            showMessage(
                "Average TCI cannot exceed Maximum TCI.",
                "result-error"
            );
            return;
        }

        // Start prediction
        button.disabled = true;
        showMessage("Calculating prediction...");

        try {
            const response = await fetch("/api/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    AverageTCI: averageTCI,
                    MaxTCI: maxTCI
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "The prediction request failed."
                );
            }

            const level = String(data.level || "").toLowerCase();

            const congestionInfo = {
                high: {
                    title: "🔴 HIGH CONGESTION",
                    className: "result-high"
                },
                medium: {
                    title: "🟠 MEDIUM CONGESTION",
                    className: "result-medium"
                },
                low: {
                    title: "🟢 LOW CONGESTION",
                    className: "result-low"
                }
            };

            const info = congestionInfo[level];

            if (!info) {
                throw new Error(
                    "The server returned an unknown congestion category."
                );
            }

            // Build the result safely
            result.replaceChildren();
            result.style.display = "block";
            result.className = info.className;

            const heading = document.createElement("h2");
            heading.textContent = info.title;

            const details = document.createElement("p");
            details.textContent =
                "Average TCI: " + averageTCI +
                " | Maximum TCI: " + maxTCI;

            const method = document.createElement("p");
            method.textContent =
                "Prediction method: " +
                (data.method || "Machine Learning model");

            const message = document.createElement("p");
            message.textContent =
                data.message || "Prediction completed successfully.";

            result.append(heading, details, method, message);

        } catch (error) {
            console.error("Prediction error:", error);

            showMessage(
                "Prediction failed: " + error.message,
                "result-error"
            );
        } finally {
            button.disabled = false;
        }
    });
});
