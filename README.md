# care-transition-efficiency-analytics
Data analytics project evaluating UAC care transition efficiency, CBP-to-HHS transfers, sponsor placement outcomes, backlog indicators, and discharge trends using Python, Pandas, and Streamlit.
# Care Transition Efficiency & Placement Outcome Analytics

## Project Overview

The **Care Transition Efficiency & Placement Outcome Analytics** project analyzes aggregate reporting data from the Unaccompanied Alien Children (UAC) Program to evaluate care transitions, operational efficiency, discharge activity, potential bottlenecks, and placement trends.

The project models the care process as a three-stage pipeline:

**CBP Custody → HHS Care → Sponsor Placement**

Using Python-based data analysis and an interactive Streamlit dashboard, the project examines how children move through the care pipeline and identifies periods of changing operational activity.

## Problem Statement

Monitoring the number of children in custody alone does not provide a complete understanding of care transition efficiency. Analyzing transfers, active care populations, and discharges together helps identify changes in pipeline activity, periods of potential accumulation, and sustained reductions in placement activity.

This project addresses the following questions:

- How efficiently are children transferred from CBP custody to HHS care?
- How do HHS care levels change over time?
- Are transfers into HHS keeping pace with discharges?
- When do periods of low discharge activity occur?
- How stable are discharge volumes across the reporting period?
- What operational indicators can help identify potential bottlenecks?

## Project Objectives

- Model the care process as a multi-stage pipeline.
- Calculate transition efficiency and discharge effectiveness metrics.
- Compare HHS inflows with successful exits.
- Identify potential accumulation and sustained low-discharge periods.
- Analyze weekday/weekend patterns and temporal trends.
- Evaluate variability and sudden changes in discharge activity.
- Develop an interactive dashboard for operational monitoring.

## Dataset Description

The dataset contains **720 valid reporting observations**, covering approximately January 2023 to December 2025.

| Column | Description |
|---|---|
| `date` | Reporting date |
| `apprehended` | Children apprehended and placed in CBP custody |
| `cbp_custody` | Children recorded in CBP custody |
| `transferred` | Children transferred from CBP custody to HHS care |
| `hhs_care` | Children recorded in HHS care |
| `discharged` | Children discharged from HHS care |

The dataset contains aggregate reporting observations rather than individual child-level records.

## Technology Stack

- **Python** – Data analysis and metric calculations
- **Pandas** – Data cleaning, transformation, and aggregation
- **NumPy** – Numerical analysis
- **Matplotlib** – Data visualization
- **Plotly** – Interactive visualizations
- **Streamlit** – Interactive analytics dashboard
- **Jupyter Notebook** – Exploratory data analysis and analytical development
- **Git and GitHub** – Version control and project documentation

## Analytical Methodology

### 1. Data Cleaning and Validation

- Remove blank rows.
- Convert reporting dates to datetime format.
- Convert numeric fields to appropriate data types.
- Validate missing values and duplicate reporting dates.
- Standardize column names for analysis.

### 2. Care Pipeline Modeling

Represent the process as:

**CBP Custody → HHS Care → Sponsor Placement**

Distinguish between stock measures, such as CBP custody and HHS care, and flow measures, such as apprehensions, transfers, and discharges.

### 3. Transition Efficiency Metrics

**Transfer Efficiency Ratio**

Transfers divided by CBP custody, expressed as a percentage.

**Discharge Effectiveness**

Discharges divided by HHS care, expressed as a percentage.

**Pipeline Throughput Rate**

Total discharges divided by total apprehensions, expressed as a percentage.

These are operational indicators and should not be interpreted as individual-level transition probabilities.

### 4. Backlog and Flow-Balance Analysis

Compare transfers into HHS care with discharges from HHS care.

**Net Flow = Transfers − Discharges**

Positive values indicate that inflows exceed exits for an observation, suggesting potential accumulation pressure. Negative values indicate that exits exceed inflows.

Cumulative net flow is used as a flow-balance indicator, not as a direct count of unresolved cases.

### 5. Temporal and Pattern Analysis

- Weekday versus weekend comparisons.
- Monthly discharge trends.
- Identification of prolonged low-discharge periods.
- Examination of changes in transfer and discharge volumes.

### 6. Outcome Stability Analysis

- Descriptive statistics for discharge volumes.
- Rolling-average analysis.
- Identification of potential sudden drops.
- Assessment of prolonged periods of low discharge activity.

## Key Findings

The analysis produced the following findings:

- **720 valid reporting observations** were analyzed.
- Total recorded apprehensions were approximately **67,337**.
- Total recorded transfers to HHS were approximately **92,641**.
- Total recorded discharges were approximately **124,853**.
- Average CBP custody was approximately **171.5 children**.
- Average HHS care was approximately **6,061.3 children**.
- The aggregate transfer efficiency ratio was approximately **75.03%**.
- The aggregate discharge effectiveness ratio was approximately **2.86%**.
- The pipeline throughput ratio was approximately **185.42%** under the defined aggregate formula.
- Discharge volume had a mean of **173.41**, a standard deviation of **125.70**, and a range of **0–505 children**.
- A substantial reduction in discharge activity was observed around early 2025.
- Six prolonged low-discharge periods were identified during 2025 using the selected stagnation threshold.
- The longest identified low-discharge period extended from **August 24 to December 21, 2025**, covering 82 reporting observations with an average of approximately 10.35 discharges per observation.

These results describe aggregate reporting patterns. They do not establish the causes of observed changes or directly measure individual reunification outcomes.

## Streamlit Dashboard

The dashboard is designed to provide interactive views of the care transition process.

### Core Modules

1. **Care Pipeline Flow Visualization**
   - View the main stages of the care pipeline.
   - Compare custody levels, transfers, HHS care, and discharges.

2. **Transfer and Discharge Efficiency**
   - Review transition efficiency metrics.
   - Compare operational indicators across reporting periods.

3. **Bottleneck and Flow-Balance Analysis**
   - Compare HHS inflows with successful exits.
   - Identify potential accumulation pressure and low-activity periods.

4. **Outcome Trend Analysis**
   - Explore monthly discharge trends.
   - Monitor rolling performance and potential sudden drops.

5. **Interactive Filtering**
   - Select a reporting date range.
   - Adjust thresholds for operational alerts.
   - Review filtered observations and relevant metrics.

## Project Structure

```text
care-transition-efficiency-analytics/
├── app.py
├── requirements.txt
├── README.md
├── notebooks/
│   └── care_transition_analysis.ipynb
├── data/
│   └── HHS_Unaccompanied_Alien_Children_Program.csv
└── reports/
    └── project_report.pdf
```

This is a suggested structure. Keep only files and folders that actually exist in your repository.

## Installation and Execution

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/care-transition-efficiency-analytics.git
cd care-transition-efficiency-analytics
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Suggested `requirements.txt`:

```text
pandas
numpy
matplotlib
plotly
streamlit
jupyter
```

### 4. Run the Dashboard

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

`http://localhost:8501`

Ensure that the CSV path in the application matches your local project structure.

## Limitations

- The dataset contains aggregate observations, not individual child-level records.
- Reporting dates are not continuous, so consecutive rows do not always represent consecutive calendar days.
- Stock-to-flow ratios are operational indicators, not individual transition probabilities.
- Cumulative net flow does not directly measure the number of unresolved cases.
- Discharge volume is used as a proxy for exits to sponsor placement; it does not independently establish individual reunification outcomes.
- Observed changes do not establish their underlying causes.

## Conclusion

This project demonstrates how data analytics can be used to evaluate care transition activity through pipeline modeling, operational metrics, flow-balance analysis, temporal analysis, and discharge stability monitoring.

The findings highlight substantial changes in care and discharge activity between 2023 and 2025, particularly the prolonged reduction in discharges during 2025. The analytical framework provides a foundation for monitoring operational patterns, identifying periods requiring further investigation, and supporting evidence-based decision-making.

## Skills Demonstrated

`Python` · `Pandas` · `NumPy` · `EDA` · `Data Cleaning` · `KPI Development` · `Time-Series Analysis` · `Data Visualization` · `Streamlit` · `Business Intelligence` · `GitHub`

---

