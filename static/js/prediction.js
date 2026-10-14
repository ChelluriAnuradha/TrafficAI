
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("predictionForm");
    const result = document.getElementById("predictionResult");
    const button = document.getElementById("predictButton");

    if (!form || !result || !button) {
        console.error("Prediction page elements not found.");
        return;
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const averageField = document.getElementById("averageTCI");
        const maxField = document.getElementById("maxTCI");

        if (!averageField || !maxField) {
            result.textContent = "Check the input IDs in predict.html.";
            return;
        }

        const averageTCI = Number(averageField.value);
        const maxTCI = Number(maxField.value);

        if (
            averageField.value.trim() === "" ||
            maxField.value.trim() === "" ||
            averageTCI < 0 ||
            maxTCI < 0 ||
            averageTCI > maxTCI
        ) {
            result.textContent =
                "Enter valid TCI values. Average TCI must not exceed Maximum TCI.";
            return;
        }

        button.disabled = true;
        result.textContent = "Calculating prediction...";

        try {
            const response = await fetch("/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    AverageTCI: averageTCI,
                    MaxTCI: maxTCI
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Prediction failed.");
            }

            const level = String(data.level || "Unknown");
            const icons = {
                High: "🔴",
                Medium: "🟠",
                Low: "🟢"
            };

            result.replaceChildren();

            const heading = document.createElement("h3");
            heading.textContent =
                (icons[level] || "🚦") + " " + level.toUpperCase() +
                " CONGESTION";

            const details = document.createElement("p");
            details.textContent =
                "Average TCI: " + averageTCI +
                " | Maximum TCI: " + maxTCI;

            const message = document.createElement("p");
            message.textContent = data.message || "Prediction completed.";

            result.append(heading, details, message);

        } catch (error) {
            result.textContent = "Prediction failed: " + error.message;
        } finally {
            button.disabled = false;
        }
    });
});
