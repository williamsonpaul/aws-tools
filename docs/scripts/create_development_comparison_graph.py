import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")  # Use non-interactive backend

# Generate feature numbers (x-axis)
features = np.arange(1, 11)

# Without Guardrails - exponential growth starting around feature 3
without_guardrails = np.array([1, 1.2, 2, 3.5, 6, 10, 16, 25, 40, 65])

# With Guardrails - slight linear increase with initial setup cost
with_guardrails = np.array([2, 2.2, 2.5, 2.8, 3.1, 3.3, 3.6, 3.8, 4.1, 4.3])

# Create the plot
plt.figure(figsize=(12, 8))
plt.plot(
    features,
    without_guardrails,
    "r-",
    linewidth=3,
    marker="o",
    markersize=8,
    label="Vibe Coding (No Guardrails)",
    alpha=0.8,
)
plt.plot(
    features,
    with_guardrails,
    "b-",
    linewidth=3,
    marker="s",
    markersize=8,
    label="Development with Guardrails",
    alpha=0.8,
)

# Customize the plot
plt.xlabel("Feature Number", fontsize=14, fontweight="bold")
plt.ylabel("Relative Time/Complexity per Feature", fontsize=14, fontweight="bold")
plt.title(
    "Development Time Comparison:\nVibe Coding vs. Automated Guardrails",
    fontsize=16,
    fontweight="bold",
    pad=20,
)

# Add grid for better readability
plt.grid(True, alpha=0.3)

# Customize legend
plt.legend(fontsize=12, loc="upper left")

# Add annotations for key points
plt.annotate(
    "Initial Setup Cost",
    xy=(1, 2),
    xytext=(1.5, 8),
    arrowprops=dict(arrowstyle="->", color="blue", alpha=0.7),
    fontsize=10,
    color="blue",
)

plt.annotate(
    'Exponential Growth\n"Whack-a-mole" Territory',
    xy=(7, 25),
    xytext=(5, 45),
    arrowprops=dict(arrowstyle="->", color="red", alpha=0.7),
    fontsize=10,
    color="red",
)

plt.annotate(
    "Crossover Point\n(Guardrails become faster)",
    xy=(3, 2.5),
    xytext=(3.5, 15),
    arrowprops=dict(arrowstyle="->", color="green", alpha=0.7),
    fontsize=10,
    color="green",
)

# Set axis limits for better visualization
plt.xlim(0.5, 10.5)
plt.ylim(0, 70)

# Add subtle background color
plt.gca().set_facecolor("#f8f9fa")

# Tight layout to prevent label cutoff
plt.tight_layout()

# Save the plot
plt.savefig("../images/development-time-comparison.png", dpi=300, bbox_inches="tight")

print("Graph saved as '../images/development-time-comparison.png'")
