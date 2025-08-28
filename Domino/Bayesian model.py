# Bayesian hierarchical model (PyMC) with a __main__ guard and smoke mode
import argparse
from multiprocessing import freeze_support
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from data_simulator import simulate_data


def run_model(
    smoke: bool = False,
    save_plot: str | None = None,
    show_plot: bool = False,
    seed: int = 123,
    likelihood: str = "student_t",
    covariates_to_use: list[str] | None = None,
    optimize_only: bool = False,
    init_with_map: bool = False,
):
    """Build, optimize, and sample the model.

    Parameters:
        smoke: If True, use a much faster sampling configuration.
        save_plot: If provided, save posterior plot to this path (non-blocking).
        show_plot: If True, display plot interactively (may block).
        seed: Random seed for reproducibility.
        likelihood: Likelihood distribution ('student_t' or 'normal').
        covariates_to_use: Specific covariates to include. Defaults to all 'x*' columns.
        optimize_only: If True, find the MAP estimate and exit without sampling.
        init_with_map: If True, find MAP and use it to initialize the sampler.
    Returns:
        trace: ArviZ InferenceData or Dict with MAP estimate
    """
    # Generate or load data
    df = simulate_data()

    # small constant to stabilize log
    eps = 1e-3
    df['y_obs'] = np.log(df['y'].clip(lower=eps) + eps)

    all_covariates = [c for c in df.columns if c.startswith('x')]
    if covariates_to_use is None:
        covariates_to_use = all_covariates
    else:
        # Validate that the user-specified covariates exist
        invalid_covs = set(covariates_to_use) - set(all_covariates)
        if invalid_covs:
            raise ValueError(f"Invalid covariates specified: {invalid_covs}")

    coords = {
        "storm": df['storm_id'].unique(),
        "polygon": df['polygon_id'].unique(),
        "covariates": covariates_to_use,
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

        # observation model (robust or normal)
        if likelihood == "student_t":
            nu = pm.Exponential("nu", 1/10)
            y_like = pm.StudentT("y_like", mu=mu, sigma=sigma_obs, nu=nu, observed=df['y_obs'].values)
        elif likelihood == "normal":
            y_like = pm.Normal("y_like", mu=mu, sigma=sigma_obs, observed=df['y_obs'].values)
        else:
            raise ValueError(f"Unsupported likelihood: {likelihood}")

        # --- Optimization Mode ---
        if optimize_only:
            print("Finding Maximum a Posteriori (MAP) estimate...")
            map_estimate = pm.find_MAP()
            print(map_estimate)
            return map_estimate

        # --- Initialization for Sampler ---
        initvals = None
        if init_with_map:
            print("Finding MAP estimate to initialize sampler...")
            initvals = pm.find_MAP()

        # --- Sampling Mode ---
        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            target_accept=target_accept,
            random_seed=seed,
            initvals=initvals,
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
    parser = argparse.ArgumentParser(description="Run, optimize, and sample a Bayesian hierarchical model.")
    parser.add_argument("--smoke", action="store_true", help="Run a quick smoke test (fast sampling)")
    parser.add_argument("--save-plot", default=None, help="Path to save posterior plot (non-blocking)")
    parser.add_argument("--show-plot", action="store_true", help="Show plot interactively (may block)")
    parser.add_argument("--seed", type=int, default=123, help="Random seed for sampling")

    # Arguments for suggestions and optimization
    parser.add_argument(
        "--likelihood",
        choices=["student_t", "normal"],
        default="student_t",
        help="Likelihood distribution for the observation model."
    )
    parser.add_argument(
        "--covariates",
        type=str,
        default=None,
        help="Comma-separated list of covariates to use (e.g., 'x1,x2'). Defaults to all."
    )
    parser.add_argument(
        "--optimize-only",
        action="store_true",
        help="Find the MAP estimate (optimization) and exit without sampling."
    )
    parser.add_argument(
        "--init-with-map",
        action="store_true",
        help="Initialize sampler with the MAP estimate to improve convergence."
    )

    args = parser.parse_args()

    # Process covariates argument
    covs = args.covariates.split(',') if args.covariates else None

    run_model(
        smoke=args.smoke,
        save_plot=args.save_plot,
        show_plot=args.show_plot,
        seed=args.seed,
        likelihood=args.likelihood,
        covariates_to_use=covs,
        optimize_only=args.optimize_only,
        init_with_map=args.init_with_map,
    )