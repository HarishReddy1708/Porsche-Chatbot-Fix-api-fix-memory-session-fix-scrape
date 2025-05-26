import re
import csv
import matplotlib.pyplot as plt
import numpy as np

# Ground truth data
ground_truth_data = {
    "911 Carrera": {"horsepower": 379, "0-60_time": 4.0, "price_usd": 114400},
    "Taycan Turbo S": {"horsepower": 750, "0-60_time": 2.6, "price_usd": 194900},
}

# Model responses
model_outputs = {
    "911 Carrera": {
        "response": "The Porsche 911 Carrera has 379 horsepower and accelerates from 0 to 60 mph in 4.1 seconds. The price starts at $114,000."
    },
    "Taycan Turbo S": {
        "response": "The Taycan Turbo S boasts 750 hp, with a 0–60 mph time of just 2.6 seconds. It costs around $195,000."
    },
}


# Function to extract numbers from response
def extract_numerical_data(response: str):
    extracted = {}
    hp_match = re.search(r"(\d{3,4})\s*(hp|horsepower)", response, re.IGNORECASE)
    if hp_match:
        extracted["horsepower"] = float(hp_match.group(1))
    accel_match = re.search(r"(\d\.\d)\s*(seconds|sec)", response, re.IGNORECASE)
    if accel_match:
        extracted["0-60_time"] = float(accel_match.group(1))
    price_match = re.search(r"\$?(\d{2,3}[,]?\d{3})", response.replace(",", ""))
    if price_match:
        extracted["price_usd"] = float(price_match.group(1))
    return extracted


# Tolerances
tolerance = {"horsepower": 5, "0-60_time": 0.2, "price_usd": 2000}

# Prepare results
results = []
for model, truth in ground_truth_data.items():
    response = model_outputs[model]["response"]
    extracted = extract_numerical_data(response)

    for metric, actual in truth.items():
        predicted = extracted.get(metric)
        error = abs(predicted - actual) if predicted is not None else None
        within_tol = error is not None and error <= tolerance[metric]
        results.append({
            "model": model,
            "metric": metric,
            "actual": actual,
            "predicted": predicted,
            "within_tolerance": within_tol,
        })

# Save to CSV
csv_file = "llm_accuracy_results.csv"
with open(csv_file, mode="w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

# Visualization — single graph
labels = []
actual_vals = []
predicted_vals = []
colors = []

for r in results:
    label = f"{r['model']} ({r['metric']})"
    labels.append(label)
    actual_vals.append(r["actual"])
    predicted_vals.append(r["predicted"] if r["predicted"] is not None else 0)
    colors.append("green" if r["within_tolerance"] else "red")

x = np.arange(len(labels))
width = 0.35

plt.figure(figsize=(12, 6))
plt.bar(x - width / 2, actual_vals, width, label="Actual", color="gray")
plt.bar(x + width / 2, predicted_vals, width, label="Predicted", color=colors)
plt.xticks(x, labels, rotation=45, ha="right")
plt.ylabel("Values")
plt.title("LLM Numerical Accuracy: Actual vs Predicted")
plt.legend()
plt.tight_layout()
plt.savefig("llm_accuracy_combined.png")
plt.show()
