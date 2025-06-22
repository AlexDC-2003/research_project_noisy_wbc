import matplotlib.pyplot as plt
import numpy as np

error_rates = [0.000001, 0.000005, 0.00001, 0.00005, 0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.05, 0.1]
failure_probs = [0.14, 0.13, 0.14, 0.1, 0.12, 0.25, 0.44, 0.73, 0.85, 1, 1, 1]

# Standard Deviation error
n = 500
stderr = [np.sqrt(p * (1 - p) / n) for p in failure_probs]

plt.figure(figsize=(8, 5))
plt.errorbar(error_rates, failure_probs, yerr=stderr, fmt='o', ecolor='gray', capsize=3, linestyle='None')
# Optional log scale for better visualization
plt.xscale('log')

# Vertical lines
plt.axvline(x=3.3e-5, color='green', linestyle='--', linewidth=1)
plt.text(3.3e-5, 0.2, 'Guba et al. Threshold', color='green', rotation=90, verticalalignment='bottom', fontsize=9)
plt.axvline(x=0.001, color='red', linestyle='--', linewidth=1)
plt.text(0.001, 0.2, 'IBM Q Best', color='red', rotation=90, verticalalignment='bottom', fontsize=9)
plt.axvline(x=0.01, color='blue', linestyle='--', linewidth=1)
plt.text(0.01, 0.2, 'IBM Q Average', color='blue', rotation=90, verticalalignment='bottom', fontsize=9)

# Horizontal lines
baseline = 0.1
baseline_error = 0.02
plt.fill_between(error_rates, 
                 [baseline - baseline_error] * len(error_rates),
                 [baseline + baseline_error] * len(error_rates),
                 color='orange', alpha=0.2, label='±0.02 uncertainty')
plt.axhline(y=baseline, color='orange', linestyle='--', linewidth=1)
plt.text(1e-5, 0.12, 'R0 faulty, error-free failure rate', color='orange', fontsize=9)

# Labels
plt.xlabel("Error Rate (Axis on Log Scale for easier visualization)")
plt.ylabel("Failure Probability")
plt.title("R0 Faulty Configuration - Failure Probability vs. Gate-Level Error Rate (m = 280)")
plt.grid(True, which='major', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.show()