import pandas as pd
import numpy as np
import re
import glob
import os
print("Current working directory:", os.getcwd())

print("Files in directory:", os.listdir('.'))



# Mapping file names to season year for later extraction
def season_from_filename(filename):
    match = re.search(r"(\d{4}-\d{4})", filename)
    return match.group(1) if match else None

# List of all files to process
files = [
    'Premier-League-Matches-2019-2020-Stats.csv',
    'Premier-League-Matches-2020-2021-Stats.csv',
    'Premier-League-Matches-2021-2022-Stats.csv',
    'Premier-League-Matches-2022-2023-Stats.csv',
    'Premier-League-Matches-2023-2024-Stats.csv',
    'Premier-League-Matches-2024-2025-Stats.csv'
]

all_dfs = []
report_rows = []

for file in files:
    df = pd.read_csv(file)
    season = season_from_filename(file)
    league = "Premier League"
    
    # Select only needed columns
    needed = {
        'date_GMT': 'Date',
        'home_team_name': 'Home_Team',
        'away_team_name': 'Away_Team',
        'Home Team Pre-Match xG': 'IGHXG',
        'Away Team Pre-Match xG': 'IGAXG',
        'total_goal_count': 'Total_Goals',
        'odds_ft_over15': 'odds_over15',
        'odds_ft_over25': 'odds_over25',
        'odds_ft_over35': 'odds_over35',
        'odds_ft_over45': 'odds_over45',
    }
    df = df[list(needed.keys())].copy()
    df.rename(columns=needed, inplace=True)

    # Convert odds columns to implied probabilities
    line_map = {1.5: 'odds_over15', 2.5: 'odds_over25', 3.5: 'odds_over35', 4.5: 'odds_over45'}
    for l, ocol in line_map.items():
        df[f'prob_over{l}'] = 1.0 / df[ocol]

    # Prepare for CTMCL calculation
    # Find the lines enclosing 50%
    ct_lines = list(line_map.keys())
    ct_probs = [f'prob_over{l}' for l in ct_lines]
    
    # Vectorized approach to calculate CTMCL
    ct_array = df[ct_probs].values
    lines_array = np.array(ct_lines)

    # For each row, find (if possible) two lines where one is just above and one just below 50%
    def find_ctmcl(row):
        probs = row[ct_probs]
        # Sort lines and probs from high line (low prob) to low line (high prob)
        order = np.argsort(-lines_array)  # 4.5, 3.5, 2.5, 1.5
        lines = lines_array[order]
        probs = probs[order]
        above = probs >= 0.5
        below = probs < 0.5
        if np.all(above):
            # All probs above 50%, pick two highest lines
            hi, lo = 0, 1
        elif np.all(below):
            # All below 50%, pick two lowest lines
            hi, lo = -2, -1
        else:
            # Normal case: find crossing
            hi = np.where(probs >= 0.5)[0][-1]
            lo = hi+1
            if lo == len(probs):
                lo = hi-1  # fallback
        line_hi, line_lo = lines[hi], lines[lo]
        prob_hi, prob_lo = probs[hi], probs[lo]
        # Linear interpolation
        if prob_hi == prob_lo:
            return np.mean([line_hi, line_lo])
        else:
            return float(line_lo + ((prob_hi-0.5) / (prob_hi-prob_lo)) * (line_hi-line_lo))

    df['CTMCL'] = df.apply(find_ctmcl, axis=1)

    # Derived columns
    df['TIGXG'] = df['IGHXG'] + df['IGAXG']
    df['Delta'] = df['TIGXG'] - df['CTMCL']
    df['Prediction'] = np.where(df['TIGXG'] > df['CTMCL'], 'Over', 'Under')
    df['Actual_Result'] = np.where(df['Total_Goals'] > df['CTMCL'], 'Over', 'Under')
    df['Score'] = (df['Prediction'] == df['Actual_Result']).astype(int)

    # Insert Season and League
    df['League'] = league
    df['Season'] = season
    cols = [
        'League', 'Season', 'Date', 'Home_Team', 'Away_Team', 'IGHXG',
        'IGAXG', 'TIGXG', 'CTMCL', 'Delta', 'Prediction', 'Total_Goals',
        'Actual_Result', 'Score'
    ]
    # Add and reorder
    all_dfs.append(df[cols])
    # Report
    n_matches = len(df)
    correct = df['Score'].sum()
    acc = correct / n_matches * 100
    report_rows.append({'Season': season, 'Matches': n_matches, 'Correct': correct, 'Accuracy': acc})

# Merge all
full_df = pd.concat(all_dfs, ignore_index=True)
full_df.to_csv('Premier League All Seasons Processed.csv', index=False)

# Accuracy report
total_matches = full_df.shape[0]
total_correct = full_df['Score'].sum()
total_acc = total_correct / total_matches * 100

print("=== Premier League Odds Assignment - Accuracy Report ===")
print(f"Total Matches: {total_matches}")
print(f"Total Correct: {total_correct}")
print(f"Overall Accuracy: {total_acc:.2f}%")
print()
print("Season-wise Breakdown:")
for row in report_rows:
    print(f"Season {row['Season']}: Matches={row['Matches']}  Correct={row['Correct']}  Accuracy={row['Accuracy']:.2f}%")

# For output
report_log = f"=== Premier League Odds Assignment - Accuracy Report ===\n"
report_log += f"Total Matches: {total_matches}\n"
report_log += f"Total Correct: {total_correct}\n"
report_log += f"Overall Accuracy: {total_acc:.2f}%\n\nSeason-wise Breakdown:\n"
for row in report_rows:
    report_log += f"Season {row['Season']}: Matches={row['Matches']}  Correct={row['Correct']}  Accuracy={row['Accuracy']:.2f}%\n"

with open('PL_CTMC_Accuracy_Report.txt', 'w') as f:
    f.write(report_log)

full_df.head(2).to_csv('PL_CTMC_FIRST2ROWS.csv', index=False)
'ready' if os.path.exists('Premier League All Seasons Processed.csv') else 'fail'
