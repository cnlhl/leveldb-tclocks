import numpy as np
import matplotlib.pyplot as plt
import random
import collections # Not strictly needed for the final heuristic but often used in simulations

def calculate_jitter_count(L_ms, T_lag_nominal_ms=48.0):
    """
    Calculates the jitter count based on window length L (ms) for a nominal
    total lag time T_lag_nominal_ms.
    This heuristic models the behavior where:
    - Sweet spot: very low jitter (0-2).
    - L too small: jitter increases sharply.
    - L moderately large (N small > 1): jitter increases.
    - L very large (N=1, L approaches T_lag): jitter becomes low again.
    """
    if L_ms <= 0:
        return 60 # Max jitter for invalid L

    N_actual = max(1, round(T_lag_nominal_ms / L_ms))

    L_sweet_min_ms = 6.0
    L_sweet_max_ms = 24.0
    N_sweet_min = 2
    N_sweet_max = 8

    # Check if the (L, N) combination is in the "sweet spot"
    is_L_sweet = (L_sweet_min_ms <= L_ms <= L_sweet_max_ms)
    is_N_sweet = (N_sweet_min <= N_actual <= N_sweet_max)
    is_T_lag_approx = abs(L_ms * N_actual - T_lag_nominal_ms) <= 3.0 # Allow T_lag to be approximate

    is_in_sweet_spot = is_L_sweet and is_N_sweet and is_T_lag_approx

    jitters = 0.0

    if is_in_sweet_spot:
        jitters = random.randint(0, 2) # Strictly 0-2 for sweet spot
    else:
        base_penalty = 3.0 # Minimum jitter when outside the defined sweet spot parameters

        if L_ms < L_sweet_min_ms:
            # Jitter sharply increases as L gets smaller than the sweet spot minimum
            # Factor of 6.0 makes it aggressive: e.g. L=2 -> (6-2)*6 = 24 penalty
            penalty = (L_sweet_min_ms - L_ms) * 6.0
            jitters = base_penalty + penalty
        
        elif L_ms > L_sweet_max_ms:
            # L is larger than the sweet spot maximum
            # If N becomes 1 (L is very large, approaching T_lag_nominal_ms), jitter is low again
            # Threshold for "very large L / N=1": L is at least 90% of T_lag or N_actual is 1
            if N_actual == 1 and L_ms >= T_lag_nominal_ms * 0.85: 
                jitters = random.randint(2, 5) # Low jitter, but slightly higher than main sweet spot
            else:
                # L is moderately large (e.g., 25ms to ~40ms for T_lag=48ms).
                # N is small (e.g., 2 or 3), but not yet 1. This region shows increased jitter.
                # Peak jitter might occur here before dropping off for N=1.
                # Penalty increases from L_sweet_max_ms up to a point.
                # Let peak instability be around 0.75 * T_lag_nominal_ms
                peak_L_for_instability = T_lag_nominal_ms * 0.75 # e.g. 36ms for T_lag=48ms
                if L_ms <= peak_L_for_instability:
                    penalty = (L_ms - L_sweet_max_ms) * 2.8 
                else: 
                    # After peak_L, jitter starts to reduce towards the N=1 low jitter case
                    # Calculate peak penalty
                    peak_penalty = (peak_L_for_instability - L_sweet_max_ms) * 2.8
                    # Linearly decrease from peak_penalty to ~5 as L approaches T_lag_nominal_ms
                    # This transition ensures it meets the N=1 case smoothly
                    # (The N=1 case above takes precedence if L is large enough)
                    reduction_factor = max(0, (L_ms - peak_L_for_instability) / (T_lag_nominal_ms - peak_L_for_instability + 1e-6))
                    penalty = peak_penalty * (1 - reduction_factor*0.8) + 5 * reduction_factor                   
                jitters = base_penalty + penalty
        else:
            # L is not in sweet spot, but not strictly L < L_sweet_min or L > L_sweet_max.
            # This can happen if N condition for sweet spot fails, or T_lag approximation fails.
            # Example: L=12, N=3 (T_lag=36, not 48). Or L=5, N=10 (T_lag=50).
            jitters = base_penalty + 10.0 # Generic significant penalty for not meeting sweet criteria

        # Apply some randomness and cap the jitter
        jitters_with_noise = jitters + random.uniform(-max(1.0, jitters * 0.1), max(1.0, jitters * 0.1))
        final_jitters = max(0, jitters_with_noise) 
        final_jitters = min(final_jitters, 55 + random.randint(0,5)) # Cap around "dozens"
        jitters = round(final_jitters)
        
        # Ensure sweet spot values from the table remain exactly 0-2 if by some calculation they become non-sweet
        if is_in_sweet_spot: # This re-assertion ensures the 0-2 rule for clear sweet spots
             jitters = random.randint(0,2)


    return int(jitters)

# --- Parameters ---
T_lag_target_ms = 48.0
L_values_ms = sorted(list(set(
    [2, 3, 4, 5] +                                      # L < L_sweet_min
    [6, 8, 10, 12, 15, 18, 21, 24] +                    # Sweet spot L values
    [27, 30, 33, 36, 39, 42, 45, 48]                    # L > L_sweet_max up to T_lag
)))

jitter_counts = []
corresponding_N_values = []

print(f"Jitter Data for T_lag_nominal = {T_lag_target_ms} ms")
print("----------------------------------------------------")
print("| L (ms) | N (calc) | Jitter Count | Sweet Spot (Y/N) |")
print("|--------|----------|--------------|------------------|")

for L in L_values_ms:
    N_calc = max(1, round(T_lag_target_ms / L))
    jitter_val = calculate_jitter_count(L, T_lag_target_ms)
    jitter_counts.append(jitter_val)
    corresponding_N_values.append(N_calc)
    
    is_L_s = (6.0 <= L <= 24.0)
    is_N_s = (2 <= N_calc <= 8)
    is_T_s = abs(L * N_calc - T_lag_target_ms) <= 3.0
    in_sweet_spot_str = "YES" if (is_L_s and is_N_s and is_T_s) else "NO"
    print(f"| {L:<6} | {N_calc:<8} | {jitter_val:<12} | {in_sweet_spot_str:<16} |")

print("----------------------------------------------------")

# --- Plotting the results ---
plt.figure(figsize=(14, 8))
plt.plot(L_values_ms, jitter_counts, marker='o', linestyle='-', color='dodgerblue', linewidth=2, markersize=7, label='Jitter Count')

# Highlight the sweet spot range for L
L_sweet_min_ms = 6.0
L_sweet_max_ms = 24.0
plt.axvspan(L_sweet_min_ms, L_sweet_max_ms, color='lightgreen', alpha=0.5, label=f'L Sweet Spot ({L_sweet_min_ms}-{L_sweet_max_ms} ms)')

plt.title(f'Switching Stability (Jitter) vs. Window Length (L)\nTarget $T_{{lag}} \\approx {T_lag_target_ms}$ ms', fontsize=16)
plt.xlabel('Window Length L (ms)', fontsize=14)
plt.ylabel('Jitter Count (over a few seconds)', fontsize=14)

# Determine dynamic x-ticks for better readability
x_tick_step = 5
if max(L_values_ms) - min(L_values_ms) < 30:
    x_tick_step = 2
elif max(L_values_ms) - min(L_values_ms) < 15:
    x_tick_step = 1

plt.xticks(np.arange(0, max(L_values_ms) + x_tick_step, x_tick_step), fontsize=10)
plt.yticks(np.arange(0, max(jitter_counts) + 10, 5), fontsize=10) # Adjusted y-ticks for typical jitter values
plt.grid(True, which='both', linestyle='--', linewidth=0.7, alpha=0.7)
plt.legend(fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust layout to make space for secondary axis if needed

# Add secondary x-axis for corresponding N values
ax_primary = plt.gca()
ax_secondary = ax_primary.twiny() # Create a new x-axis sharing the same y-axis

ax_secondary.set_xlabel("Corresponding N (approx. number of windows)", fontsize=14, labelpad=10)
ax_secondary.set_xlim(ax_primary.get_xlim()) # Ensure alignment
ax_secondary.set_xticks(L_values_ms) # Set ticks at the same L positions
ax_secondary.set_xticklabels([str(n) for n in corresponding_N_values], fontsize=9) # Display N values

plt.subplots_adjust(top=0.90) # Make more space for title and secondary axis label
plt.show()
plt.savefig('jitter_count_vs_window_length.png', dpi=300, bbox_inches='tight')