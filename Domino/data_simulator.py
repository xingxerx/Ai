# Simulate N events and perform power calc via repeated fits
import numpy as np
import pandas as pd

def simulate_data(n_events=60, polygons_per_event=3, baseline_mean=100, sd_within=80,
                  treatment_effect=-0.15, intrastorm_sd=30):
    rows = []
    for s in range(n_events):
        for p in range(polygons_per_event):
            # randomize treatment at storm-level block or polygon-level
            t = np.random.choice([0,1])  # adapt to block design
            storm_noise = np.random.normal(0, intrastorm_sd)
            y = np.random.normal(baseline_mean*(1 + storm_noise/100.0), sd_within)
            y = max(y, 0.0)
            if t == 1:
                y = y * (1 + treatment_effect)
            rows.append({'storm_id': s, 'polygon_id': f"{s}_{p}", 't': t, 'y': y, 'x1': np.random.normal()})
    return pd.DataFrame(rows)

# perform many simulations, fit simplified model (e.g. with PyMC or a frequentist mixed model),
# and compute proportion of sims where posterior CI excludes 0 or p-value < 0.05.
