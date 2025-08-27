# Bayesian hierarchical model (PyMC) with a __main__ guard and smoke mode
import argparse
from multiprocessing import freeze_support
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from data_simulator import simulate_data


def run_model(smoke: bool = False, save_plot: str | None = None, show_plot: bool = False, seed: int = 123):
    """Build and sample the model.

    Parameters:
        smoke: If True, use a much faster sampling configuration.
        save_plot: If provided, save posterior plot to this path (non-blocking).
        show_plot: If True, display plot interactively (may block).
        seed: Random seed for reproducibility.
    Returns:
        trace: ArviZ InferenceData
    """
    # Generate or load data
    df = simulate_data()

    # small constant to stabilize log
    eps = 1e-3
    df['y_obs'] = np.log(df['y'].clip(lower=eps) + eps)

    coords = {
        "storm": df['storm_id'].unique(),
        "polygon": df['polygon_id'].unique(),
        "covariates": [c for c in df.columns if c.startswith('x')]
    }

    draws, tune, chains, target_accept = (200, 200, 2, 0.90) if smoke else (2000, 1000, 4, 0.95)

    with pm.Model(coords=coords) as model:
        # hyperpriors
        sigma_storm = pm.Exponential("sigma_storm", 1.0)
        sigma_polygon = pm.Exponential("sigma_polygon", 1.0)
        sigma_obs = pm.Exponential("sigma_obs", 1.0)

        # random effects
        storm_idx = pd.Categorical(df['storm_id'], categories=coords['storm']).codes
        polygon_idx = pd.Categorical(df['polygon_id'], categories=coords['polygon']).codes

        a_storm = pm.Normal("a_storm", mu=0.0, sigma=sigma_storm, dims="storm")
        a_polygon = pm.Normal("a_polygon", mu=0.0, sigma=sigma_polygon, dims="polygon")

        # covariate coefficients
        cov_names = coords['covariates']
        beta_cov = pm.Normal("beta_cov", mu=0.0, sigma=1.0, shape=len(cov_names))

        # treatment effect (primary parameter)
        beta_t = pm.Normal("beta_t", mu=0.0, sigma=1.0)

        # linear predictor
        X = df[cov_names].values
        mu = (a_storm[storm_idx] + a_polygon[polygon_idx]
              + (X * beta_cov).sum(axis=1)
              + beta_t * df['t'].values)

        # observation model (robust)
        nu = pm.Exponential("nu", 1/10)
        y_like = pm.StudentT("y_like", mu=mu, sigma=sigma_obs, nu=nu, observed=df['y_obs'].values)

        # posterior
        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            target_accept=target_accept,
            random_seed=seed,
            cores=1,
        )

    # Summaries (print to console)
    summary = az.summary(trace, var_names=["beta_t", "beta_cov", "sigma_obs", "sigma_storm", "sigma_polygon"])
    try:
        # Pretty print if available
        print(summary.to_string(max_rows=20))
    except Exception:
        print(summary)

    # Plot handling: avoid blocking by default; save if requested
    if save_plot or show_plot:
        import matplotlib
        if not show_plot:
            # Non-interactive backend to prevent blocking
            matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt

        az.plot_posterior(trace, var_names=["beta_t"])
        if save_plot:
            plt.savefig(save_plot, bbox_inches="tight")
            print(f"Saved posterior plot to: {save_plot}")
        if show_plot:
            plt.show()
        plt.close('all')

    return trace


if __name__ == "__main__":
    freeze_support()
    parser = argparse.ArgumentParser(description="Run Bayesian hierarchical model.")
    parser.add_argument("--smoke", action="store_true", help="Run a quick smoke test (fast sampling)")
    parser.add_argument("--save-plot", default=None, help="Path to save posterior plot (non-blocking)")
    parser.add_argument("--show-plot", action="store_true", help="Show plot interactively (may block)")
    parser.add_argument("--seed", type=int, default=123, help="Random seed for sampling")
    args = parser.parse_args()

    run_model(smoke=args.smoke, save_plot=args.save_plot, show_plot=args.show_plot, seed=args.seed)