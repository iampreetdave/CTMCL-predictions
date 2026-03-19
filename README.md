# CTMCL Predictions

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)

> Analyzes Premier League seasons by calculating a Consensus Total Market Goals Line (CTMCL) from betting odds and comparing it to expected goals (xG) to predict Over/Under outcomes.

## About

This project introduces the CTMCL (Consensus Total Market Goals Line) method — a novel approach to football match prediction. It derives a custom total goals line from over/under betting odds using linear interpolation, then compares it against pre-match xG (expected goals) data to predict whether a match will go Over or Under. The project also includes a Random Forest Classifier variant that trains on historical features for enhanced prediction accuracy. Built for sports analytics research and model evaluation across six Premier League seasons (2019–2025).

## Tech Stack

- **Language:** Python 3
- **Libraries:** Pandas, NumPy, scikit-learn

## Features

- **CTMCL calculation** from over/under betting odds via linear interpolation at the 50% implied probability crossing
- **xG-based prediction** — compares total implied xG against the CTMCL to determine Over/Under
- **Random Forest Classifier** — ML model trained on xG, CTMCL, odds, and derived features
- **Multi-season analysis** — processes six Premier League seasons (2019–2025)
- **Accuracy reporting** — season-wise and overall accuracy breakdowns
- **CSV output** — full processed dataset with predictions and scores

## Getting Started

### Prerequisites

- Python 3.7+
- pandas, numpy, scikit-learn

### Installation

```bash
git clone https://github.com/iampreetdave/CTMCL-predictions.git
cd CTMCL-predictions
pip install pandas numpy scikit-learn
```

### Run

**Basic CTMCL analysis:**

```bash
python ctmcl.py
```

**Random Forest Classifier model:**

```bash
python CTMCL-ML-RFC.py
```

## How It Works

1. **Data Loading:** Reads per-season Premier League CSV files containing match stats, xG, goals, and betting odds
2. **CTMCL Calculation:** Converts over/under odds (1.5, 2.5, 3.5, 4.5) to implied probabilities, finds the two lines that straddle 50%, and interpolates a custom total goals line
3. **Prediction:** Compares total pre-match xG (home + away) against the CTMCL — if xG > CTMCL, predict Over; otherwise Under
4. **ML Enhancement:** The RFC variant trains a Random Forest on engineered features (xG, CTMCL, delta, odds, home/away win odds) for binary Over/Under classification
5. **Evaluation:** Computes accuracy per season and overall, outputs full results to CSV

## Project Structure

```
CTMCL-predictions/
├── ctmcl.py                                    # Core CTMCL analysis script
├── CTMCL-ML-RFC.py                             # Random Forest Classifier variant
├── Premier-League-Matches-*-Stats.csv           # Season data files (2019–2025)
├── Premier League All Seasons Processed.csv     # Output: full processed results
├── PL_CTMC_Accuracy_Report.txt                  # Output: accuracy report
├── PL_CTMC_FIRST2ROWS.csv                       # Output: sample preview
└── README.md
```

## License

This project is licensed under the [MIT License](LICENSE).
