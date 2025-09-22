# Premier League Odds Assignment  

## 📂 Folder Contents  
This folder contains multiple CSV files with Premier League match statistics:  

- `Premier League Matches 2019-2020 Stats.csv`  
- `Premier League Matches 2020-2021 Stats.csv`  
- `Premier League Matches 2021-2022 Stats.csv`  
- `Premier League Matches 2022-2023 Stats.csv`  
- `Premier League Matches 2023-2024 Stats.csv`  
- `Premier League Matches 2024-2025 Stats.csv`  

Your task is to process these files, calculate a **CTMCL metric (Closing Total Market Consensus Line)**, and evaluate predictions based on it.  

---

## 📝 Task Instructions  

### Step 1: Columns to Use  
From each input CSV, you will use the following columns:  

- `date_GMT` → Date  
- `home_team_name` → Home_Team  
- `away_team_name` → Away_Team  
- `Home Team Pre-Match xG` → IGHXG  
- `Away Team Pre-Match xG` → IGAXG  
- `total_goal_count` → Total_Goals  
- Odds columns for interpolation:  
  - `odds_ft_over15`  
  - `odds_ft_over25`  
  - `odds_ft_over35`  
  - `odds_ft_over45`  

### Step 2: CTMCL Calculation  
- Convert each decimal odd into **implied probability**:  

  Implied Probability = 1 / (Decimal Odd)

- Identify the two lines that straddle **50% probability** (e.g., Over 3.5 = 54.6% and Over 4.5 = 35.1%).  
- Perform **linear interpolation**:  

  CTMCL = Lower Line + ((P_above - 0.5) / (P_above - P_below)) × (Higher Line - Lower Line)

- Example:  
  - Over 3.5 = 54.6%  
  - Over 4.5 = 35.1%  
  - CTMCL ≈ 3.74 goals  

### Step 3: Derived Columns  
After calculating CTMCL, derive the following:  

- **TIGXG** = IGHXG + IGAXG  
- **Delta** = TIGXG – CTMCL  
- **Prediction** = "Over" if TIGXG > CTMCL else "Under"  
- **Actual_Result** = "Over" if Total_Goals > CTMCL else "Under"  
- **Score** = 1 if Prediction == Actual_Result else 0  

### Step 4: Final Output Columns  
Your final processed dataset should have the following columns (in this order):  

1. League (always "Premier League")  
2. Season (extract from filename, e.g., `2019-2020`)  
3. Date  
4. Home_Team  
5. Away_Team  
6. IGHXG  
7. IGAXG  
8. TIGXG  
9. CTMCL  
10. Delta  
11. Prediction  
12. Total_Goals  
13. Actual_Result  
14. Score  

### Step 5: Deliverables  
1. A single merged file:  
   - `Premier League All Seasons Processed.csv`  
   - This should contain **all seasons combined** with the above columns.  

2. Accuracy report (print in terminal):  
   - Total matches across all seasons  
   - Correct predictions across all seasons  
   - Overall accuracy %  
   - Season-wise breakdown (Matches, Correct, Accuracy %)  

---

## ✅ Expected Example Output (Format)  

| League         | Season    | Date              | Home_Team         | Away_Team        | IGHXG | IGAXG | TIGXG | CTMCL  | Delta | Prediction | Total_Goals | Actual_Result | Score |  
|----------------|-----------|-------------------|------------------|-----------------|-------|-------|-------|--------|-------|------------|-------------|---------------|-------|  
| Premier League | 2019-2020 | Aug 09 2019 7:00pm | Liverpool        | Norwich City     | 1.83  | 1.32  | 3.15  | 3.00   | 0.15  | Over       | 5           | Over          | 1     |  
| Premier League | 2019-2020 | Aug 10 2019 11:30am | West Ham United | Manchester City  | 0.98  | 1.87  | 2.85  | 2.90   | -0.05 | Under      | 5           | Over          | 0     |  

---

## 📩 Submission  
- Return the **processed CSV file** (`Premier League All Seasons Processed.csv`).  
- Share the **accuracy report screenshot or log** showing total and per-season accuracy.  
- Deadline: **End of Day**.  
