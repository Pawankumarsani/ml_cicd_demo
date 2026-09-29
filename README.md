# ML CI/CD Demo

[![CD Pipeline](https://github.com/Pawankumarsani/ml_cicd_demo/actions/workflows/cd.yml/badge.svg)](https://github.com/Pawankumarsani/ml_cicd_demo/actions/workflows/cd.yml)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

An end-to-end demonstration of a **machine learning CI/CD pipeline** — training, automated testing, and containerized delivery, fully automated with GitHub Actions and Docker Hub.

The model itself is deliberately trivial (a linear regression fit on synthetic data). The point of this repo is everything *around* the model — because that's the part that actually decides whether an ML project can be shipped and maintained by a team, or dies as a notebook.

## How it works

Every push to `main` triggers a two-stage pipeline in GitHub Actions:

```
 push to main
      │
      ▼
┌──────────────────────────────────────────────────────┐
│  Job 1: train-and-test                               │
│                                                      │
│  checkout → Python 3.11 → pip install →             │
│  python train.py  →  pytest test_model.py -v         │
│                    (fails if R² < 0.85)               │
└──────────────────────┬───────────────────────────────┘
                       │ only if tests passed
                       ▼
┌──────────────────────────────────────────────────────┐
│  Job 2: build-and-push                               │
│                                                      │
│  docker login (secrets) → build image →              │
│  push to pawan407/ml-cicd-demo:latest                │
└──────────────────────────────────────────────────────┘
```

The key design decision is the **quality gate**: the Docker image is only built
and pushed if the test job succeeds. A regression that drops model quality
below the threshold (`R² < 0.85` on freshly generated, unseen data) blocks the
release instead of silently shipping a degraded model.

## Repository structure

```text
ml_cicd_demo/
├── train.py                  # trains the model, saves model.pkl
├── test_model.py             # pytest: R² must stay above 0.85 on new data
├── requirements.txt          # scikit-learn, joblib, numpy, pytest
├── Dockerfile                # slim Python 3.11 image that runs training
└── .github/
    └── workflows/
        └── cd.yml            # the two-stage pipeline shown above
```

## What each piece does

**`train.py`** — generates synthetic data (`y = 2.5x + 1.2` + noise), fits a
`LinearRegression`, saves the model to `model.pkl` with joblib, and prints the
training R².

**`test_model.py`** — a pytest that loads `model.pkl` and scores it on a *new*
batch of randomly generated data. It asserts `R² > 0.85`, so it's a genuine
functional gate, not just a smoke test that the code runs.

**`Dockerfile`** — builds a minimal `python:3.11-slim` image, installs the
dependencies, and runs the training script as the container entrypoint.

**`cd.yml`** — the pipeline. `build-and-push` has `needs: train-and-test`, so
a failed test run means no image is published. Docker Hub credentials come
from repository secrets, never from the repo itself.

## Run it locally

```bash
git clone https://github.com/Pawankumarsani/ml_cicd_demo.git
cd ml_cicd_demo
pip install -r requirements.txt

# train
python train.py
# Model trained. R² on training data: ~0.99

# test
pytest test_model.py -v
```

## Run the Docker image

```bash
docker pull pawan407/ml-cicd-demo:latest
docker run --rm pawan407/ml-cicd-demo:latest
```

The container trains the model from scratch and prints the R² — proof that
the published image is self-contained.

## Use this pipeline for your own project

1. Fork or copy the repo structure.
2. In **Settings → Secrets and variables → Actions**, add:
   - `DOCKER_USERNAME` — your Docker Hub username
   - `DOCKERHUB_TOKEN` — an access token from Docker Hub (Account Settings → Security)
3. Change the image tag in `cd.yml` (`pawan407/ml-cicd-demo:latest`) to your
   own `<dockerhub-username>/<repo-name>:latest`.
4. Replace `train.py` / `test_model.py` with your model and a meaningful
   quality threshold — the pipeline structure stays the same.

## Possible next steps

- Tag images with the commit SHA (`:sha-<short_sha>` alongside `:latest`) so
  every release is traceable back to a commit
- Add a model registry step (MLflow / Weights & Biases) instead of committing `model.pkl`
- Add a deploy stage (e.g. push the served model to a cloud endpoint)
- Add linting/type-checking (`ruff`, `mypy`) as an earlier pipeline gate
