# Greening-process

Code for the temperature surrogate and greening planner in *"Updating greening plans during implementation delivers cooling worth nearly a third more new green space"*.

The planner greens a city unit by unit under two rules:

- **Blueprint**: every allocation is chosen on the initial city.
- **Adaptive**: each allocation is chosen on the landscape left by completed units.

## Install

```bash
pip install -r requirements.txt
```

Requires Python 3 with NumPy, SciPy and PyTorch. A GPU is recommended.

## Input

Put one `.npz` file per city in an input folder. Each file contains:

- `landcover`, `ndvi`, `height` (building height, m), `building` (0/1), `urban` (0/1): 10 m grid
- `lst`: land-surface temperature on the nested 30 m grid
- `climate`: city climate features
- `city_id` (optional)

The 10 m grid dimensions must be multiples of 3. Land-cover classes 0–2 are treated as green and classes 3–4 as eligible for greening (see `config.json`).

## Usage

```bash
# Train the surrogate and evaluate it on held-out spatial blocks
python run.py train --input data/cities --output runs/surrogate

# Plan every city under the blueprint and adaptive rules
python run.py plan --input data/cities --checkpoint runs/surrogate/model.pt --output runs/plan --route heat
```

`--route` can be `heat`, `cool` or `random`; random routes also take `--route-seed`. Model, training and planning settings are in `config.json` and are saved with the trained model. Evaluation and planning must use the same input files as training.

## Output

For each city, `plan` writes:

- `initial.npz`: predicted temperature of the initial city and planning-unit IDs
- `blueprint.npz` and `adaptive.npz`: final green allocation and predicted temperature

## Files

- `run.py`: command-line entry
- `config.json`: settings
- `greening/data.py`: data loading and preprocessing
- `greening/model.py`: U-Net temperature surrogate
- `greening/engine.py`: training and evaluation
- `greening/planning.py`: planning units, allocation optimisation and the two rules
