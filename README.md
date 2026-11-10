# nyc-taxi-crawl

*Will this taxi trip crawl through traffic?* At pickup, we predict whether a New York yellow taxi trip will average under 6 mph, so that a dispatcher can warn the passenger.

Project 1 of the Machine Learning course at University Metropolitan Tirana (question C, "The crawl").

## Result

| Model | June PR AUC | July PR AUC (scored once) |
|---|---|---|
| Baseline: decision tree, depth 2 | 0.339 | — |
| **Logistic regression** (distance, time, zones) | **0.632** | **0.627** (95% interval 0.621–0.632) |

About one trip in five crawls. With the warning threshold chosen from the costs of each mistake (0.30), the model catches 78% of July's crawls, and 47% of its warnings are real crawls. It works best for daytime trips in Manhattan and worst at night.

## How to run it

Requires Python 3.11 or newer. From a terminal:


git clone <repository URL>
cd nyc-taxi-crawl
python -m venv .venv

Activate the environment:

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- macOS / Linux: `source .venv/bin/activate`

Then install the libraries and download the data (about 17 MB, into `data/raw/`):

python -m pip install -r requirements.txt
python data/get_data.py


Open the notebooks in VS Code or Jupyter, select the `.venv` kernel, and run them *in order*, each with *Restart → Run All*. Each one rebuilds what it needs from the raw data; nothing has to be saved in between.

## Notebooks

| Notebook | What it does |
|---|---|
| [`01-frame.ipynb`](notebooks/01-frame.ipynb) | The target, which trips can be labelled (with the positive rate after each rule), the split and the baseline ladder |
| [`02-clean-and-split.ipynb`](notebooks/02-clean-and-split.ipynb) | Audit of the raw data, a fix / flag / drop decision for each problem, and the analysis: hour, day, zone map, which trips crawl, stability by month |
| [`03-features.ipynb`](notebooks/03-features.ipynb) | Feature groups added one at a time and judged on June; logistic regression against decision trees |
| [`04-evaluate.ipynb`](notebooks/04-evaluate.ipynb) | Threshold from costs, reliability diagram, slices, and the single look at July |

The shared code lives in `src/`: `data.py` (loading, labelling and splitting), `features.py` (features and pipelines) and `evaluate.py` (metrics).

## Key decisions

- *Split by month:* May trains, June validates every decision, July is scored once.
- *Only information known at pickup:* pickup time, the two zones and the trip distance, treated as the planned route. The drop-off time, fares and anything settled at the end are never model inputs. See [`PROBLEM.md`](PROBLEM.md).
- *Trips whose speed cannot be trusted are dropped* (durations under 1 minute or over 2 hours, zero or absurd distances, speeds of 70 mph or more): 5% of the trips.
- *Flex fare trips are kept*, because the dispatcher would face them in practice.

## Data

[NYC Taxi & Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) yellow taxi trip records, May to July 2026, as a 600,000-trip sample prepared for the course. The data is downloaded by `data/get_data.py` and never committed.

## Team

Diego Jove Villanueva and Carlos del Rio de Paz

## Use of AI

We used Claude (Anthropic) as a tutor and assistant throughout the project: to explain concepts, review our decisions, and help write and debug code and notebook text. Every member has read and can explain every part of the repository.
