# Bayesian hierarchical model (PyMC)
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az

# df: pandas DataFrame with columns ['y','t','storm_id','polygon_id','x1',...]
# small constant to stabilize log
eps = 1e-3
df['y_obs'] = np.log(df['y'].clip(lower=eps) + eps)

coords = {
    "storm": df['storm_id'].unique(),
    "polygon": df['polygon_id'].unique(),
    "covariates": [c for c in df.columns if c.startswith('x')]
}

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
    trace = pm.sample(draws=2000, tune=1000, chains=4, target_accept=0.95)

# Summaries
az.summary(trace, var_names=["beta_t", "beta_cov", "sigma_obs", "sigma_storm", "sigma_polygon"])
az.plot_posterior(trace, var_names=["beta_t"])
