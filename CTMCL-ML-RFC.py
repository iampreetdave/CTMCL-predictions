import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# Files and columns as before
files = [
    ('Premier-League-Matches-2019-2020-Stats.csv', '2019-2020'),
    ('Premier-League-Matches-2020-2021-Stats.csv', '2020-2021'),
    ('Premier-League-Matches-2021-2022-Stats.csv', '2021-2022'),
    ('Premier-League-Matches-2022-2023-Stats.csv', '2022-2023'),
    ('Premier-League-Matches-2023-2024-Stats.csv', '2023-2024'),
    ('Premier-League-Matches-2024-2025-Stats.csv', '2024-2025')
]

cols_to_use = [
    'date_GMT', 'home_team_name', 'away_team_name',
    'Home Team Pre-Match xG', 'Away Team Pre-Match xG', 'total_goal_count',
    'odds_ft_over15', 'odds_ft_over25', 'odds_ft_over35', 'odds_ft_over45',
    'odds_ft_home_team_win', 'odds_ft_away_team_win'
]

# Load and concat all data
all_seasons = []
for file, season in files:
    df = pd.read_csv(file, usecols=cols_to_use)
    df['Season'] = season
    all_seasons.append(df)

data = pd.concat(all_seasons, ignore_index=True)

# Drop NaNs from key columns
data = data.dropna(subset=[
    'date_GMT', 'home_team_name', 'away_team_name', 'Home Team Pre-Match xG',
    'Away Team Pre-Match xG', 'total_goal_count',
    'odds_ft_over15', 'odds_ft_over25', 'odds_ft_over35', 'odds_ft_over45'
])

data = data.rename(columns={
    'date_GMT': 'Date',
    'home_team_name': 'Home_Team',
    'away_team_name': 'Away_Team',
    'Home Team Pre-Match xG': 'IGHXG',
    'Away Team Pre-Match xG': 'IGAXG',
    'total_goal_count': 'Total_Goals'
})

def implied_prob(odd):
    try:
        odd_f = float(odd)
        if odd_f <= 1:
            return np.nan
        return 1 / odd_f
    except:
        return np.nan

for col in ['odds_ft_over15', 'odds_ft_over25', 'odds_ft_over35', 'odds_ft_over45']:
    data[f'prob_{col}'] = data[col].apply(implied_prob)

def calculate_ctmcl(row):
    lines = [1.5, 2.5, 3.5, 4.5]
    probs = [row['prob_odds_ft_over15'], row['prob_odds_ft_over25'],
             row['prob_odds_ft_over35'], row['prob_odds_ft_over45']]

    filtered = [(l, p) for l, p in zip(lines, probs) if not pd.isna(p)]
    if len(filtered) < 2:
        return np.nan

    lower_line = None
    upper_line = None
    lower_prob = None
    upper_prob = None

    for i in range(len(filtered) - 1):
        l1, p1 = filtered[i]
        l2, p2 = filtered[i + 1]
        if p1 >= 0.5 >= p2:
            lower_line, lower_prob = l2, p2
            upper_line, upper_prob = l1, p1
            break

    if lower_line is None or upper_line is None:
        if filtered[0][1] < 0.5:
            return filtered[0][0]
        if filtered[-1][1] > 0.5:
            return filtered[-1][0]
        return np.nan

    ctmcl = lower_line + ((0.5 - lower_prob) / (upper_prob - lower_prob)) * (upper_line - lower_line)
    if ctmcl < 0:
        return np.nan

    return round(ctmcl, 2)

data['CTMCL'] = data.apply(calculate_ctmcl, axis=1)
data['TIGXG'] = data['IGHXG'] + data['IGAXG']
data['Delta'] = data['TIGXG'] - data['CTMCL']
data = data.dropna(subset=['CTMCL'])

features = data[
    ['IGHXG', 'IGAXG', 'TIGXG', 'CTMCL', 'Delta',
     'odds_ft_home_team_win', 'odds_ft_away_team_win',
     'odds_ft_over15', 'odds_ft_over25', 'odds_ft_over35', 'odds_ft_over45']
]

data['Target'] = (data['Total_Goals'] > data['CTMCL']).astype(int)

X_train, X_test, y_train, y_test = train_test_split(features, data['Target'], test_size=0.2, random_state=42)

# Scale features - optional for tree-based models, but sometimes useful
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Random Forest Classifier
rfc = RandomForestClassifier(n_estimators=200, random_state=42)
rfc.fit(X_train_scaled, y_train)

y_pred = rfc.predict(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)
print(f'Random Forest Test Accuracy: {accuracy:.4f}')
print('Classification Report:')
print(classification_report(y_test, y_pred))

data['League'] = 'Premier League'
features_scaled = scaler.transform(features)
data['RFC_Prediction'] = rfc.predict(features_scaled)
data['RFC_Score'] = (data['RFC_Prediction'] == data['Target']).astype(int)

overall_accuracy_rfc = data['RFC_Score'].mean() * 100
print(f'Overall Random Forest Accuracy on Full Dataset: {overall_accuracy_rfc:.2f}%')

final_cols = [
    'League', 'Season', 'Date', 'Home_Team', 'Away_Team',
    'IGHXG', 'IGAXG', 'TIGXG', 'CTMCL', 'Delta',
    'Total_Goals', 'Target', 'RFC_Prediction', 'RFC_Score',
    'odds_ft_home_team_win', 'odds_ft_away_team_win',
    'odds_ft_over45', 'odds_ft_over15', 'odds_ft_over25', 'odds_ft_over35'
]

final_data = data[final_cols]
final_data.to_csv('Premier League All Seasons Processed with RFC.csv', index=False)


# After training Random Forest Classifier (rfc) and making full predictions as before:

# Assign Prediction column as Over/Under based on RFC predicted classes
data['Prediction'] = np.where(data['RFC_Prediction'] == 1, 'Over', 'Under')

# Compute Actual_Result based on Total_Goals vs CTMCL
data['Actual_Result'] = np.where(data['Total_Goals'] > data['CTMCL'], 'Over', 'Under')

# Compute Score as 1 if Prediction == Actual_Result else 0
data['Score'] = (data['Prediction'] == data['Actual_Result']).astype(int)

# Add League column
data['League'] = 'Premier League'

# Prepare final columns in order
final_columns = [
    'League', 'Season', 'Date', 'Home_Team', 'Away_Team',
    'IGHXG', 'IGAXG', 'TIGXG', 'CTMCL', 'Delta',
    'Prediction',  # using RFC predictions as final Prediction
    'Total_Goals', 'Actual_Result', 'RFC_Score',  # RFC_Score as Score
    'odds_ft_home_team_win', 'odds_ft_away_team_win',
    'odds_ft_over45', 'odds_ft_over15', 'odds_ft_over25', 'odds_ft_over35'
]
final_output = data[final_columns]

# Save to CSV
final_output.to_csv('Premier  RFC sus2.csv', index=False)
