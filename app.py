import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================
      
st.set_page_config(
    page_title="Care Transition Efficiency Analytics",
    page_icon="🏥",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    file_path = "HHS_Unaccompanied_Alien_Children_Program.csv"

    df = pd.read_csv(file_path)

    # Remove completely empty rows
    df = df.dropna(how="all").copy()

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert date
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Convert numeric columns
    numeric_columns = [
        "Children apprehended and placed in CBP custody*",
        "Children in CBP custody",
        "Children transferred out of CBP custody",
        "Children in HHS Care",
        "Children discharged from HHS Care"
    ]

    for col in numeric_columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
        )

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # Rename columns
    df = df.rename(columns={
        "Date": "date",
        "Children apprehended and placed in CBP custody*": "apprehended",
        "Children in CBP custody": "cbp_custody",
        "Children transferred out of CBP custody": "transferred",
        "Children in HHS Care": "hhs_care",
        "Children discharged from HHS Care": "discharged"
    })

    # Remove rows with invalid dates
    df = df.dropna(subset=["date"])

    # Sort chronologically
    df = df.sort_values("date").reset_index(drop=True)

    # --------------------------------------------------------
    # DERIVED METRICS
    # --------------------------------------------------------

    # Transfer Efficiency
    df["transfer_efficiency"] = np.where(
        df["cbp_custody"] > 0,
        df["transferred"] / df["cbp_custody"],
        np.nan
    )

    # Discharge Effectiveness
    df["discharge_effectiveness"] = np.where(
        df["hhs_care"] > 0,
        df["discharged"] / df["hhs_care"],
        np.nan
    )

    # Percentage versions
    df["transfer_efficiency_pct"] = (
        df["transfer_efficiency"] * 100
    )

    df["discharge_effectiveness_pct"] = (
        df["discharge_effectiveness"] * 100
    )

    # HHS net flow
    df["net_flow"] = (
        df["transferred"] - df["discharged"]
    )

    # Flow status
    df["flow_status"] = np.select(
        [
            df["net_flow"] > 0,
            df["net_flow"] < 0
        ],
        [
            "Accumulation Pressure",
            "Backlog Reduction"
        ],
        default="Balanced"
    )

    # Month
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # Day information
    df["day_type"] = np.where(
        df["date"].dt.dayofweek >= 5,
        "Weekend",
        "Weekday"
    )

    return df


df = load_data()


# ============================================================
# HEADER
# ============================================================

st.title("🏥 Care Transition Efficiency & Placement Outcome Analytics")

st.markdown(
    """
    **CBP Custody → HHS Care → Sponsor Placement**

    This dashboard analyzes transition efficiency, discharge performance,
    backlog pressure, bottlenecks, and placement outcomes over time.
    """
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Dashboard Controls")


# ------------------------------------------------------------
# DATE RANGE
# ------------------------------------------------------------

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date, end_date = date_range

    filtered_df = df[
        (df["date"].dt.date >= start_date) &
        (df["date"].dt.date <= end_date)
    ].copy()

else:

    filtered_df = df.copy()


# ------------------------------------------------------------
# METRIC TOGGLE
# ------------------------------------------------------------

st.sidebar.subheader("Metric Selection")

metric_option = st.sidebar.radio(
    "Select Efficiency Metric",
    [
        "Transfer Efficiency",
        "Discharge Effectiveness",
        "Both"
    ]
)


# ------------------------------------------------------------
# ALERT THRESHOLDS
# ------------------------------------------------------------

st.sidebar.subheader("Alert Thresholds")

transfer_threshold = st.sidebar.slider(
    "Minimum Transfer Efficiency (%)",
    min_value=0,
    max_value=100,
    value=50,
    step=5
)

discharge_threshold = st.sidebar.slider(
    "Minimum Discharge Effectiveness (%)",
    min_value=0,
    max_value=20,
    value=2,
    step=1
)

backlog_threshold = st.sidebar.number_input(
    "Backlog Pressure Threshold",
    min_value=0,
    value=50,
    step=10
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_apprehended = filtered_df["apprehended"].sum()
total_transferred = filtered_df["transferred"].sum()
total_discharged = filtered_df["discharged"].sum()

avg_cbp = filtered_df["cbp_custody"].mean()
avg_hhs = filtered_df["hhs_care"].mean()

# Weighted transfer efficiency
transfer_efficiency = np.nan

if filtered_df["cbp_custody"].sum() > 0:

    transfer_efficiency = (
        filtered_df["transferred"].sum()
        /
        filtered_df["cbp_custody"].sum()
    ) * 100


# Weighted discharge effectiveness
discharge_effectiveness = np.nan

if filtered_df["hhs_care"].sum() > 0:

    discharge_effectiveness = (
        filtered_df["discharged"].sum()
        /
        filtered_df["hhs_care"].sum()
    ) * 100


# Pipeline throughput
pipeline_throughput = np.nan

if total_apprehended > 0:

    pipeline_throughput = (
        total_discharged /
        total_apprehended
    ) * 100


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Executive KPIs")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Entries",
    f"{total_apprehended:,.0f}"
)

col2.metric(
    "Total Transfers",
    f"{total_transferred:,.0f}"
)

col3.metric(
    "Total Discharges",
    f"{total_discharged:,.0f}"
)

col4.metric(
    "Transfer Efficiency",
    f"{transfer_efficiency:.2f}%"
)

col5.metric(
    "Discharge Effectiveness",
    f"{discharge_effectiveness:.2f}%"
)


st.divider()


# ============================================================
# MODULE 1
# CARE PIPELINE FLOW VISUALIZATION
# ============================================================

st.header("1️⃣ Care Pipeline Flow Visualization")

st.markdown(
    """
    **CBP Custody → HHS Care → Sponsor Placement**
    """
)


# ------------------------------------------------------------
# PIPELINE SANKEY
# ------------------------------------------------------------

sankey_fig = go.Figure(
    go.Sankey(
        arrangement="snap",

        node=dict(
            label=[
                "CBP Custody",
                "HHS Care",
                "Sponsor Placement"
            ],
            pad=30,
            thickness=25
        ),

        link=dict(
            source=[0, 1],
            target=[1, 2],
            value=[
                total_transferred,
                total_discharged
            ]
        )
    )
)

sankey_fig.update_layout(
    title="Care Pipeline Movement",
    height=450
)

st.plotly_chart(
    sankey_fig,
    use_container_width=True
)


# ------------------------------------------------------------
# PIPELINE STOCKS OVER TIME
# ------------------------------------------------------------

pipeline_plot = go.Figure()

pipeline_plot.add_trace(
    go.Scatter(
        x=filtered_df["date"],
        y=filtered_df["cbp_custody"],
        mode="lines",
        name="CBP Custody"
    )
)

pipeline_plot.add_trace(
    go.Scatter(
        x=filtered_df["date"],
        y=filtered_df["hhs_care"],
        mode="lines",
        name="HHS Care"
    )
)

pipeline_plot.update_layout(
    title="Care Pipeline Stock Levels Over Time",
    xaxis_title="Date",
    yaxis_title="Children",
    hovermode="x unified"
)

st.plotly_chart(
    pipeline_plot,
    use_container_width=True
)


# ============================================================
# MODULE 2
# TRANSFER & DISCHARGE EFFICIENCY
# ============================================================

st.header("2️⃣ Transfer & Discharge Efficiency")


# ------------------------------------------------------------
# METRIC DATA
# ------------------------------------------------------------

if metric_option == "Transfer Efficiency":

    efficiency_fig = px.line(
        filtered_df,
        x="date",
        y="transfer_efficiency_pct",
        title="Transfer Efficiency Over Time",
        labels={
            "transfer_efficiency_pct": "Transfer Efficiency (%)",
            "date": "Date"
        }
    )

    efficiency_fig.add_hline(
        y=transfer_threshold,
        line_dash="dash",
        annotation_text="Alert Threshold"
    )

    st.plotly_chart(
        efficiency_fig,
        use_container_width=True
    )


elif metric_option == "Discharge Effectiveness":

    efficiency_fig = px.line(
        filtered_df,
        x="date",
        y="discharge_effectiveness_pct",
        title="Discharge Effectiveness Over Time",
        labels={
            "discharge_effectiveness_pct":
                "Discharge Effectiveness (%)",
            "date": "Date"
        }
    )

    efficiency_fig.add_hline(
        y=discharge_threshold,
        line_dash="dash",
        annotation_text="Alert Threshold"
    )

    st.plotly_chart(
        efficiency_fig,
        use_container_width=True
    )


else:

    efficiency_fig = go.Figure()

    efficiency_fig.add_trace(
        go.Scatter(
            x=filtered_df["date"],
            y=filtered_df["transfer_efficiency_pct"],
            mode="lines",
            name="Transfer Efficiency"
        )
    )

    efficiency_fig.add_trace(
        go.Scatter(
            x=filtered_df["date"],
            y=filtered_df["discharge_effectiveness_pct"],
            mode="lines",
            name="Discharge Effectiveness"
        )
    )

    efficiency_fig.update_layout(
        title="Transfer & Discharge Efficiency",
        xaxis_title="Date",
        yaxis_title="Efficiency (%)",
        hovermode="x unified"
    )

    st.plotly_chart(
        efficiency_fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# EFFICIENCY SUMMARY
# ------------------------------------------------------------

eff_col1, eff_col2, eff_col3 = st.columns(3)

eff_col1.metric(
    "Transfer Efficiency",
    f"{transfer_efficiency:.2f}%"
)

eff_col2.metric(
    "Discharge Effectiveness",
    f"{discharge_effectiveness:.2f}%"
)

eff_col3.metric(
    "Pipeline Throughput",
    f"{pipeline_throughput:.2f}%"
)


# ============================================================
# MODULE 3
# BOTTLENECK DETECTION
# ============================================================

st.header("3️⃣ Bottleneck Detection")


# ------------------------------------------------------------
# NET FLOW
# ------------------------------------------------------------

bottleneck_fig = go.Figure()

bottleneck_fig.add_trace(
    go.Bar(
        x=filtered_df["date"],
        y=filtered_df["net_flow"],
        name="Net Flow"
    )
)

bottleneck_fig.add_hline(
    y=backlog_threshold,
    line_dash="dash",
    annotation_text="Accumulation Alert"
)

bottleneck_fig.add_hline(
    y=-backlog_threshold,
    line_dash="dash",
    annotation_text="Reduction Alert"
)

bottleneck_fig.update_layout(
    title="Daily HHS Net Flow: Transfers − Discharges",
    xaxis_title="Date",
    yaxis_title="Net Flow",
    hovermode="x unified"
)

st.plotly_chart(
    bottleneck_fig,
    use_container_width=True
)


# ------------------------------------------------------------
# IDENTIFY ALERT PERIODS
# ------------------------------------------------------------

filtered_df["bottleneck_alert"] = (
    filtered_df["net_flow"] >= backlog_threshold
)

alert_df = filtered_df[
    filtered_df["bottleneck_alert"]
].copy()


if len(alert_df) > 0:

    st.warning(
        f"⚠️ {len(alert_df)} reporting observations "
        f"exceeded the backlog-pressure threshold."
    )

    st.dataframe(
        alert_df[
            [
                "date",
                "transferred",
                "discharged",
                "net_flow",
                "hhs_care"
            ]
        ].sort_values(
            "net_flow",
            ascending=False
        ),
        use_container_width=True
    )

else:

    st.success(
        "No reporting observations exceeded "
        "the selected backlog-pressure threshold."
    )


# ------------------------------------------------------------
# TOP BOTTLENECK OBSERVATIONS
# ------------------------------------------------------------

st.subheader("Highest Accumulation-Pressure Observations")

top_bottlenecks = filtered_df.nlargest(
    10,
    "net_flow"
)

st.dataframe(
    top_bottlenecks[
        [
            "date",
            "transferred",
            "discharged",
            "net_flow",
            "hhs_care"
        ]
    ],
    use_container_width=True
)


# ============================================================
# MODULE 4
# OUTCOME TREND ANALYSIS
# ============================================================

st.header("4️⃣ Outcome Trend Analysis")


# ------------------------------------------------------------
# MONTHLY PLACEMENTS
# ------------------------------------------------------------

monthly = (
    filtered_df
    .groupby("month")
    .agg(
        total_discharges=("discharged", "sum"),
        average_discharges=("discharged", "mean"),
        total_transfers=("transferred", "sum"),
        average_hhs_care=("hhs_care", "mean")
    )
    .reset_index()
)

monthly["mom_change_pct"] = (
    monthly["total_discharges"]
    .pct_change()
    * 100
)


# ------------------------------------------------------------
# PLACEMENT TREND
# ------------------------------------------------------------

placement_fig = px.line(
    monthly,
    x="month",
    y="total_discharges",
    markers=True,
    title="Month-over-Month Sponsor Placement Trend",
    labels={
        "month": "Month",
        "total_discharges": "Total Discharges"
    }
)

st.plotly_chart(
    placement_fig,
    use_container_width=True
)


# ------------------------------------------------------------
# MOM CHANGE
# ------------------------------------------------------------

mom_fig = px.bar(
    monthly,
    x="month",
    y="mom_change_pct",
    title="Month-over-Month Change in Discharges",
    labels={
        "month": "Month",
        "mom_change_pct": "MoM Change (%)"
    }
)

mom_fig.add_hline(
    y=0,
    line_dash="dash"
)

st.plotly_chart(
    mom_fig,
    use_container_width=True
)


# ============================================================
# OUTCOME STABILITY
# ============================================================

st.subheader("Outcome Stability")

discharge_mean = filtered_df["discharged"].mean()
discharge_std = filtered_df["discharged"].std()

if discharge_mean > 0:

    discharge_cv = (
        discharge_std /
        discharge_mean
    )

    stability_score = (
        1 /
        (1 + discharge_cv)
    )

else:

    discharge_cv = np.nan
    stability_score = np.nan


stab1, stab2, stab3 = st.columns(3)

stab1.metric(
    "Average Discharges",
    f"{discharge_mean:,.2f}"
)

stab2.metric(
    "Discharge CV",
    f"{discharge_cv:.2f}"
)

stab3.metric(
    "Outcome Stability Score",
    f"{stability_score:.3f}"
)


# ============================================================
# SUDDEN DROP DETECTION
# ============================================================

filtered_df["rolling_discharge"] = (
    filtered_df["discharged"]
    .rolling(7)
    .mean()
)

filtered_df["drop_vs_rolling_pct"] = (
    (
        filtered_df["discharged"]
        -
        filtered_df["rolling_discharge"]
    )
    /
    filtered_df["rolling_discharge"]
) * 100

filtered_df["sudden_drop"] = (
    filtered_df["drop_vs_rolling_pct"] <= -30
)


drop_df = filtered_df[
    filtered_df["sudden_drop"]
].copy()


st.subheader("Potential Sudden Drops in Placement Outcomes")


if len(drop_df) > 0:

    st.warning(
        f"⚠️ {len(drop_df)} reporting observations "
        "showed discharges at least 30% below "
        "their 7-observation rolling average."
    )

    st.dataframe(
        drop_df[
            [
                "date",
                "discharged",
                "rolling_discharge",
                "drop_vs_rolling_pct"
            ]
        ],
        use_container_width=True
    )

else:

    st.success(
        "No potential sudden drops were detected "
        "using the selected rule."
    )


# ============================================================
# WEEKDAY VS WEEKEND
# ============================================================

st.header("📅 Weekday vs Weekend Analysis")

weekday_analysis = (
    filtered_df
    .groupby("day_type")
    .agg(
        observations=("date", "count"),
        avg_transfers=("transferred", "mean"),
        avg_discharges=("discharged", "mean"),
        avg_transfer_efficiency=(
            "transfer_efficiency_pct",
            "mean"
        ),
        avg_discharge_effectiveness=(
            "discharge_effectiveness_pct",
            "mean"
        )
    )
    .reset_index()
)

st.dataframe(
    weekday_analysis,
    use_container_width=True
)


# ============================================================
# DATA TABLE
# ============================================================

with st.expander("🔎 View Filtered Dataset"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Care Transition Efficiency & Placement Outcome Analytics | "
    "CBP → HHS → Sponsor Placement"
)