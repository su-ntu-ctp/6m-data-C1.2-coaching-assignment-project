import json
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "SGJobData_cleaned.csv")

# Palette (validated categorical set, fixed order — see dataviz skill)
CATEGORICAL_PALETTE = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]
OTHER_COLOR = "#898781"  # muted gray, reserved for the "Other" bucket
TEXT_PRIMARY = "#0b0b0b"
SURFACE = "#fcfcfb"
GRIDLINE = "#e1e0d9"
PIE_TOP_N = 8
CATEGORY_SALARY_TOP_N = 10

TABLE_COLS = [
    "postedCompany_name",
    "positionLevels",
    "title",
    "numberOfVacancies",
    "employmentTypes",
    "minimumYearsExperience",
    "salary_maximum",
    "salary_minimum",
    "average_salary",
    "metadata_jobPostId",
    "metadata_totalNumberJobApplication",
    "metadata_totalNumberOfView",
]

LOAD_COLS = [
    "postedCompany_name",
    "positionLevels",
    "title",
    "numberOfVacancies",
    "salary_maximum",
    "salary_minimum",
    "average_salary",
    "employmentTypes",
    "categories",
    "minimumYearsExperience",
    "status_jobStatus",
    "metadata_isPostedOnBehalf",
    "metadata_jobPostId",
    "metadata_totalNumberJobApplication",
    "metadata_totalNumberOfView",
    "metadata_repostCount",
    "metadata_originalPostingDate",
]

JOB_STATUS_ORDER = ["Open", "Re-open", "Closed"]

st.set_page_config(page_title="Singapore Jobs Market Intelligence Product", layout="wide")


@st.cache_data(show_spinner="Loading job data...")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=LOAD_COLS)

    df["categories"] = df["categories"].astype("string").str.strip()
    df["category_names"] = df["categories"].apply(
        lambda x: [c["category"] for c in json.loads(x)] if x else []
    )
    df = df.drop(columns=["categories"])

    df["metadata_originalPostingDate"] = pd.to_datetime(
        df["metadata_originalPostingDate"], errors="coerce"
    )

    return df


df = load_data(CSV_PATH)

st.title("Singapore Jobs Market Intelligence Data Product")
st.caption("Filter job postings on the left to explore matching roles.")

# ---- Sidebar filters ----
st.sidebar.header("Filters")

sal_min_bound = int(df["salary_minimum"].min())
sal_min_upper = int(df["salary_minimum"].max())
salary_minimum_floor = st.sidebar.number_input(
    "Salary minimum (at least)",
    min_value=sal_min_bound,
    max_value=sal_min_upper,
    value=sal_min_bound,
    step=100,
)
st.sidebar.caption(f"${salary_minimum_floor:,}")

sal_max_bound = int(df["salary_maximum"].min())
sal_max_upper = int(df["salary_maximum"].max())
salary_maximum_ceiling = st.sidebar.number_input(
    "Salary maximum (at most)",
    min_value=sal_max_bound,
    max_value=sal_max_upper,
    value=sal_max_upper,
    step=100,
)
st.sidebar.caption(f"${salary_maximum_ceiling:,}")

avg_sal_bound = int(df["average_salary"].min())
avg_sal_upper = int(df["average_salary"].max())
average_salary_floor = st.sidebar.number_input(
    "Average salary (at least)",
    min_value=avg_sal_bound,
    max_value=avg_sal_upper,
    value=avg_sal_bound,
    step=100,
)
st.sidebar.caption(f"${average_salary_floor:,}")

employment_types = sorted(df["employmentTypes"].dropna().unique())
selected_employment_types = st.sidebar.multiselect(
    "Employment types", options=employment_types, default=[]
)

all_categories = sorted({c for cats in df["category_names"] for c in cats})


def _apply_select_all_categories():
    st.session_state["categories_multiselect"] = all_categories
    st.session_state["select_all_categories_cb"] = False


st.sidebar.checkbox(
    "Select all categories",
    key="select_all_categories_cb",
    on_change=_apply_select_all_categories,
)
if "categories_multiselect" not in st.session_state:
    st.session_state["categories_multiselect"] = all_categories
selected_categories = st.sidebar.multiselect(
    "Categories", options=all_categories, key="categories_multiselect"
)

position_levels = sorted(df["positionLevels"].dropna().unique())
selected_position_levels = st.sidebar.multiselect(
    "Position levels", options=position_levels, default=[]
)

exp_bound = int(df["minimumYearsExperience"].min())
exp_upper = int(df["minimumYearsExperience"].max())
minimum_experience = st.sidebar.number_input(
    "Minimum years experience (at least)",
    min_value=exp_bound,
    max_value=exp_upper,
    value=exp_bound,
    step=1,
)
maximum_experience = st.sidebar.number_input(
    "Minimum years experience (at most)",
    min_value=exp_bound,
    max_value=exp_upper,
    value=exp_upper,
    step=1,
)

present_statuses = set(df["status_jobStatus"].dropna().unique())
job_statuses = [s for s in JOB_STATUS_ORDER if s in present_statuses] + sorted(
    present_statuses - set(JOB_STATUS_ORDER)
)
selected_job_statuses = st.sidebar.multiselect(
    "Job status", options=job_statuses, default=[]
)

posted_on_behalf = st.sidebar.selectbox(
    "Posted on behalf", options=["All", "True", "False"], index=0
)

time_range_granularity = st.sidebar.radio(
    "Time range granularity",
    options=["Year/Month", "Year/Quarter"],
    index=0,
    horizontal=True,
)
time_range_freq = "M" if time_range_granularity == "Year/Month" else "Q"

posting_periods = pd.period_range(
    df["metadata_originalPostingDate"].min().to_period(time_range_freq),
    df["metadata_originalPostingDate"].max().to_period(time_range_freq),
    freq=time_range_freq,
)
period_labels = [str(p) for p in posting_periods]
time_range_start_label, time_range_end_label = st.sidebar.select_slider(
    "Time Range",
    options=period_labels,
    value=(period_labels[0], period_labels[-1]),
    key=f"time_range_slider_{time_range_freq}",
)
time_range_start = pd.Period(time_range_start_label, freq=time_range_freq).start_time
time_range_end = pd.Period(time_range_end_label, freq=time_range_freq).end_time

# ---- Apply filters ----
mask = pd.Series(True, index=df.index)
mask &= df["salary_minimum"] >= salary_minimum_floor
mask &= df["salary_maximum"] <= salary_maximum_ceiling
mask &= df["minimumYearsExperience"] >= minimum_experience
mask &= df["minimumYearsExperience"] <= maximum_experience
mask &= df["average_salary"] >= average_salary_floor

if selected_employment_types:
    mask &= df["employmentTypes"].isin(selected_employment_types)

if selected_categories:
    mask &= df["category_names"].apply(
        lambda cats: any(c in selected_categories for c in cats)
    )

if selected_position_levels:
    mask &= df["positionLevels"].isin(selected_position_levels)

if selected_job_statuses:
    mask &= df["status_jobStatus"].isin(selected_job_statuses)

if posted_on_behalf != "All":
    mask &= df["metadata_isPostedOnBehalf"] == (posted_on_behalf == "True")

mask &= df["metadata_originalPostingDate"] >= time_range_start
mask &= df["metadata_originalPostingDate"] <= time_range_end

filtered = df.loc[mask, TABLE_COLS].reset_index(drop=True)

# ---- KPI row ----
total_vacancies = filtered["numberOfVacancies"].sum()
weighted_avg_salary = (
    (filtered["average_salary"] * filtered["numberOfVacancies"]).sum() / total_vacancies
    if total_vacancies
    else None
)

total_applications = filtered["metadata_totalNumberJobApplication"].sum()
total_views = filtered["metadata_totalNumberOfView"].sum()
competition_index = total_applications / total_vacancies if total_vacancies else None

COMPETITION_INDEX_COLOR = "#4a3aa7"  # violet accent, sets this derived metric apart from the rest

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
col1.metric("Matching postings", f"{len(filtered):,}")
col2.metric(
    "Average salary",
    f"${weighted_avg_salary:,.0f}" if weighted_avg_salary is not None else "—",
)
col3.metric("Companies", f"{filtered['postedCompany_name'].nunique():,}")
col4.metric("Total job applications", f"{total_applications:,.0f}")
col5.metric("Total views", f"{total_views:,.0f}")
col6.metric("Total vacancies", f"{total_vacancies:,.0f}")
with col7:
    st.markdown(
        f"""
        <div style="display:flex; flex-direction:column; gap:2px;">
            <div style="font-size:0.875rem; color:rgba(11,11,11,0.6);">Competition index</div>
            <div style="font-size:2.25rem; font-weight:600; line-height:1.2; color:{COMPETITION_INDEX_COLOR};">
                {f"{competition_index:,.1f}" if competition_index is not None else "—"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Total job applications ÷ total vacancies for the filtered postings — "
        "how many applicants are competing per opening. Higher = more competitive."
    )

st.divider()

# ---- Business Q1-4: industry breakdowns (scoped to selected Categories) ----


SEQUENTIAL_SALARY_SCALE = [[0, "#dbe9fa"], [1, CATEGORICAL_PALETTE[0]]]
SEQUENTIAL_BLUE_SCALE = SEQUENTIAL_SALARY_SCALE
SEQUENTIAL_PURPLE_SCALE = [[0, "#ded8f5"], [1, CATEGORICAL_PALETTE[6]]]
SEQUENTIAL_RED_SCALE = [[0, "#f8d9d8"], [1, CATEGORICAL_PALETTE[7]]]


def make_metric_bar(
    series: pd.Series,
    colorscale,
    value_format: str,
    xaxis_title: str,
) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=series.values,
            y=series.index,
            orientation="h",
            marker=dict(
                color=series.values,
                colorscale=colorscale,
                cornerradius=4,
                showscale=False,
            ),
            text=[value_format.format(v) for v in series.values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>%{x:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        template="plotly_dark",
        height=600,
        bargap=0.35,
        margin=dict(l=10, r=70, t=40, b=10),
        xaxis=dict(title=xaxis_title, tickformat=",.0f"),
        yaxis=dict(title=None, categoryorder="total ascending"),
    )
    return fig


def make_category_salary_bar(series: pd.Series) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=series.values,
            y=series.index,
            orientation="h",
            marker=dict(
                color=series.values,
                colorscale=SEQUENTIAL_SALARY_SCALE,
                cornerradius=4,
            ),
            text=[f"${v:,.0f}" for v in series.values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>Avg salary: $%{x:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=max(320, 40 * len(series)),
        bargap=0.35,
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font=dict(color=TEXT_PRIMARY, family="system-ui, -apple-system, sans-serif"),
        margin=dict(l=10, r=70, t=10, b=10),
        xaxis=dict(
            title="Average salary ($)",
            gridcolor=GRIDLINE,
            zeroline=False,
            tickformat="$,.0f",
        ),
        yaxis=dict(title=None),
    )
    return fig


def render_category_chart(agg: pd.Series, build_chart) -> None:
    if len(agg):
        st.plotly_chart(build_chart(agg), width="stretch")
    elif not selected_categories:
        st.info("Select one or more categories on the left to compare them here.")
    else:
        st.info("No postings match the current filters.")


category_rows = (
    df.loc[
        mask,
        [
            "category_names",
            "average_salary",
            "numberOfVacancies",
            "metadata_totalNumberJobApplication",
            "metadata_repostCount",
        ],
    ]
    .explode("category_names")
    .dropna(subset=["category_names"])
)
category_rows = category_rows[category_rows["category_names"].isin(selected_categories)]

category_agg = category_rows.groupby("category_names").agg(
    avg_salary=("average_salary", "mean"),
    total_vacancies=("numberOfVacancies", "sum"),
    total_applications=("metadata_totalNumberJobApplication", "sum"),
    total_reposts=("metadata_repostCount", "sum"),
)

st.subheader("💰 Business Question 1")
st.markdown(
    """
### Which industries offer the highest average salaries?

This visualization compares the **average monthly salary** across industries
to identify the highest-paying sectors, among the categories selected on the left.
"""
)
category_salary = (
    category_agg["avg_salary"]
    .sort_values(ascending=False)
    .head(CATEGORY_SALARY_TOP_N)
    .sort_values(ascending=True)
)
render_category_chart(category_salary, make_category_salary_bar)

top_salary_industry = None
if len(category_salary):
    top_ranked = category_salary.sort_values(ascending=False)
    highest_name, highest_salary = top_ranked.index[0], top_ranked.iloc[0]
    top_salary_industry = highest_name
    runner_up_lines = "".join(
        f"<li>{name} — ${salary:,.0f}</li>"
        for name, salary in top_ranked.iloc[1:3].items()
    )
    st.markdown(
        f"""
<div style="
background-color:#184d2b;
padding:20px;
border-radius:10px;
border-left:6px solid #4CAF50;
">
<h3 style="color:#7CFC98;">📊 Business Insight</h3>
<p style="font-size:19px; color:white;">
The <b>{highest_name}</b> industry offers the highest average monthly salary among
the selected categories, at approximately
<span style="font-size:24px; font-weight:bold; color:#FFD54F;">
S${highest_salary:,.0f}
</span>
</p>
<ul style="font-size:16px; color:white;">
{runner_up_lines}
</ul>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("---")
st.subheader("💼 Business Question 2")
st.markdown(
    """
### Which industries have the greatest hiring demand?

This visualization compares the **number of open vacancies** across industries
to identify the sectors with the highest hiring activity, among the categories selected on the left.
"""
)
st.subheader("💼 Hiring Demand by Industry")
vacancies_by_category = (
    category_agg["total_vacancies"].sort_values(ascending=False).head(CATEGORY_SALARY_TOP_N)
)
render_category_chart(
    vacancies_by_category,
    lambda s: make_metric_bar(
        s.sort_values(ascending=True),
        SEQUENTIAL_BLUE_SCALE,
        "{:,.0f}",
        "Number of open vacancies",
    ),
)

if len(vacancies_by_category):
    ranked = vacancies_by_category.sort_values(ascending=False)
    highest_name, highest_val = ranked.index[0], ranked.iloc[0]
    second_name, second_val = ranked.index[1], ranked.iloc[1]
    third_name, third_val = ranked.index[2], ranked.iloc[2]
    st.markdown(
        f"""
<div style="
background-color:#184d2b;
padding:20px;
border-radius:10px;
border-left:6px solid #4CAF50;
">
<h3 style="color:#7CFC98;">📈 Business Insight</h3>
<p style="font-size:19px; color:white;">
The <b>{highest_name}</b> industry has the highest hiring demand with
<span style="font-size:24px; font-weight:bold; color:#FFD54F;">
{highest_val:,.0f}
</span>
open vacancies.
</p>
<p style="font-size:18px; color:white;">
It is followed by
<b>{second_name}</b>
<span style="font-size:18px; font-weight:bold; color:#FFD54F;">
{second_val:,.0f}
</span> vacancies and
<b>{third_name}</b>
<span style="font-size:18px; font-weight:bold; color:#FFD54F;">
{third_val:,.0f}
</span> vacancies.
</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("---")
st.subheader("📥 Business Question 3")
st.markdown(
    """
### Which industries receive the most applications?
"""
)
st.write(
    "This visualization compares the total number of applications received across industries."
)
st.subheader("Application Trend 📥")
applications_by_category = (
    category_agg["total_applications"].sort_values(ascending=False).head(CATEGORY_SALARY_TOP_N)
)
render_category_chart(
    applications_by_category,
    lambda s: make_metric_bar(
        s.sort_values(ascending=True),
        SEQUENTIAL_PURPLE_SCALE,
        "{:,.0f}",
        "Number of applications",
    ),
)

if len(applications_by_category):
    ranked = applications_by_category.sort_values(ascending=False)
    highest_name, highest_val = ranked.index[0], ranked.iloc[0]
    second_name, second_val = ranked.index[1], ranked.iloc[1]
    third_name, third_val = ranked.index[2], ranked.iloc[2]
    st.markdown(
        f"""
<div style="
background-color:#184d2b;
padding:20px;
border-radius:10px;
border-left:6px solid #4CAF50;
">
<h3 style="color:#7CFC98;">📈 Business Insight</h3>
<p style="font-size:19px; color:white;">
The <b>{highest_name}</b> industry attracts the highest number of job applications
<span style="font-size:24px; font-weight:bold; color:#FFD54F;">
{highest_val:,.0f}
</span> indicating the strongest demand from job seekers.
</p>
<p style="font-size:18px; color:white;">
It is followed by
<b>{second_name}</b>
<span style="font-size:18px; font-weight:bold; color:#FFD54F;">
{second_val:,.0f}
</span> applications and
<b>{third_name}</b>
<span style="font-size:18px; font-weight:bold; color:#FFD54F;">
{third_val:,.0f}
</span> applications.
</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("---")
st.subheader("🔍 Business Question 4")
st.markdown(
    """
### Which industries are hardest to fill?
"""
)
st.write(
    "This visualization compares total repost counts across industries — how often employers had to relist a vacancy."
)
st.subheader("Competition Index 🔍")
reposts_by_category = (
    category_agg["total_reposts"].sort_values(ascending=False).head(CATEGORY_SALARY_TOP_N)
)
render_category_chart(
    reposts_by_category,
    lambda s: make_metric_bar(
        s.sort_values(ascending=True),
        SEQUENTIAL_RED_SCALE,
        "{:,.0f}",
        "Total repost count",
    ),
)

if len(reposts_by_category):
    ranked = reposts_by_category.sort_values(ascending=False)
    highest_name, highest_val = ranked.index[0], ranked.iloc[0]
    second_name, second_val = ranked.index[1], ranked.iloc[1]
    third_name, third_val = ranked.index[2], ranked.iloc[2]
    st.markdown(
        f"""
<div style="
background-color:#184d2b;
padding:20px;
border-radius:10px;
border-left:6px solid #4CAF50;
">
<h3 style="color:#7CFC98;">📈 Business Insight</h3>
<p style="font-size:19px; color:white;">
The <b>{highest_name}</b> industry has the highest repost count
<span style="font-size:24px; font-weight:bold; color:#FFD54F;">
{highest_val:,.0f}
</span> indicating it is comparatively harder to fill than other industries.
</p>
<p style="font-size:18px; color:white;">
It is followed by
<b>{second_name}</b>
<span style="font-size:18px; font-weight:bold; color:#FFD54F;">
{second_val:,.0f}
</span> and
<b>{third_name}</b>
<span style="font-size:18px; font-weight:bold; color:#FFD54F;">
{third_val:,.0f}
</span> reposts.
</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("---")
st.subheader("🔍 Business Question 5")
st.markdown(
    """
### How has hiring changed over time?
"""
)
st.write("This visualization checks the hiring trend over time.")
st.subheader("Hiring Trend 🔍")


def make_time_bar(series: pd.Series) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=series.index,
            y=series.values,
            mode="lines+markers",
            line=dict(color="#00B4D8", width=4),
            marker=dict(size=8),
            hovertemplate="%{x}<br>%{y:,.0f} postings<extra></extra>",
        )
    )
    fig.update_layout(
        template="plotly_dark",
        height=500,
        margin=dict(l=10, r=20, t=40, b=10),
        title="Hiring Trend",
        xaxis=dict(title="Period"),
        yaxis=dict(title="Number of job postings"),
    )
    return fig


q5_view = st.radio(
    "View",
    options=["Year/Quarter", "Last 15 months"],
    index=0,
    horizontal=True,
    key="q5_view",
)

if q5_view == "Year/Quarter":
    latest_quarter = pd.Period(time_range_end, freq="Q")
    last_five_quarters = pd.period_range(latest_quarter - 4, latest_quarter, freq="Q")

    postings_by_period = (
        df.loc[mask, "metadata_originalPostingDate"].dropna().dt.to_period("Q").value_counts()
    )
    postings_by_period = postings_by_period.reindex(last_five_quarters, fill_value=0)
    postings_by_period.index = [f"{q.year} Q{q.quarter}" for q in last_five_quarters]

    st.caption(
        f"Last 5 calendar quarters ending {last_five_quarters[-1].year} Q{last_five_quarters[-1].quarter} "
        "(the upper bound of the Time Range filter)."
    )
else:
    latest_month = pd.Period(time_range_end, freq="M")
    last_fifteen_months = pd.period_range(latest_month - 14, latest_month, freq="M")

    postings_by_period = (
        df.loc[mask, "metadata_originalPostingDate"].dropna().dt.to_period("M").value_counts()
    )
    postings_by_period = postings_by_period.reindex(last_fifteen_months, fill_value=0)
    postings_by_period.index = [p.strftime("%Y-%m") for p in last_fifteen_months]

    st.caption(
        f"Last 15 months ending {last_fifteen_months[-1].strftime('%Y-%m')} "
        "(the upper bound of the Time Range filter)."
    )

if postings_by_period.sum():
    st.plotly_chart(make_time_bar(postings_by_period), width="stretch")

    ranked_periods = postings_by_period.sort_values(ascending=False)
    if len(ranked_periods) >= 3:
        highest_name, highest_val = ranked_periods.index[0], ranked_periods.iloc[0]
        second_name, second_val = ranked_periods.index[1], ranked_periods.iloc[1]
        third_name, third_val = ranked_periods.index[2], ranked_periods.iloc[2]
        st.markdown(
            f"""
<div style="
background-color:#184d2b;
padding:20px;
border-radius:10px;
border-left:6px solid #4CAF50;
">
<h3 style="color:#7CFC98;">📈 Business Insight</h3>
<p style="font-size:19px; color:white;">
Hiring activity <b>peaked in {highest_name}</b> with
<span style="font-size:24px; font-weight:bold; color:#FFD54F;">
{highest_val:,.0f}
</span>
job postings.
</p>
<p style="font-size:18px; color:white;">
The next strongest periods were
<b>{second_name}</b>
(<span style="color:#FFD54F;">{second_val:,.0f}</span>)
and
<b>{third_name}</b>
(<span style="color:#FFD54F;">{third_val:,.0f}</span>),
indicating sustained recruitment demand during this period.
</p>
</div>
""",
            unsafe_allow_html=True,
        )
else:
    st.info("No postings match the current filters.")

top_salary_industry_label = top_salary_industry or "the top-paying industries"
st.markdown(
    f"""
<div style="
background-color:#153B73;
padding:25px;
border-radius:10px;
border-left:8px solid #5DADE2;
">

<h2 style="color:#A9D6FF; font-size:34px;">
📌 Key Business Conclusions:
</h2>

<div style="font-size:24px; color:white; line-height:2.0;">
💰<b>{top_salary_industry_label}</b> offers the highest average monthly salary.
</div>

<div style="font-size:24px; color:white; line-height:2.0; margin-top:15px;">
💼 Hiring demand remains strong across key industries, with sustained recruitment activity over time.
</div>

<div style="font-size:24px; color:white; line-height:2.0; margin-top:15px;">
📥Competition differs significantly across industries, indicating varying levels of job seeker interest.
</div>

<div style="font-size:24px; color:white; line-height:2.0; margin-top:15px;">
🔍This dashboard enables interactive exploration of salary, hiring demand, competition, and employment patterns to support informed career and business decisions.
</div>

</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# ---- Pie charts ----
st.subheader("Breakdown of matching postings")


def make_pie(series: pd.Series, title: str) -> go.Figure:
    counts = series.dropna().value_counts()
    if len(counts) > PIE_TOP_N:
        top = counts.iloc[:PIE_TOP_N]
        other_total = counts.iloc[PIE_TOP_N:].sum()
        counts = pd.concat([top, pd.Series({"Other": other_total})])

    colors = CATEGORICAL_PALETTE[: len(counts)]
    if "Other" in counts.index:
        colors = colors[: len(counts) - 1] + [OTHER_COLOR]

    total = counts.sum()
    legend_labels = [
        f"{name} — {value / total:.1%} ({value:,})"
        for name, value in counts.items()
    ]

    fig = go.Figure(
        go.Pie(
            labels=legend_labels,
            values=counts.values,
            marker=dict(colors=colors, line=dict(color=SURFACE, width=2)),
            textinfo="none",
            hovertext=counts.index,
            hovertemplate="%{hovertext}<br>%{percent} — %{value:,} postings<extra></extra>",
            sort=False,
        )
    )
    fig.update_layout(
        title=title,
        height=420,
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font=dict(color=TEXT_PRIMARY, family="system-ui, -apple-system, sans-serif"),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="v", yanchor="middle", y=0.5, font=dict(size=11)),
    )
    return fig


if len(filtered):
    pie_col1, pie_col2 = st.columns(2)
    with pie_col1:
        st.plotly_chart(
            make_pie(filtered["positionLevels"], "Position level"),  use_container_width=True
            #width="stretch"
        )
    with pie_col2:
        st.plotly_chart(
            make_pie(filtered["employmentTypes"], "Employment type"), width="stretch"
        )
else:
    st.info("No postings match the current filters.")

# ---- Main table ----
st.divider()
st.subheader("Job postings")

table_col1, table_col2 = st.columns([3, 1])
title_search = table_col1.text_input("Filter by title contains", value="", placeholder="e.g. engineer")
show_job_post_id = table_col2.checkbox("Show Job Post ID", value=False)

if title_search:
    filtered = filtered[filtered["title"].str.contains(title_search, case=False, na=False)]

table_column_order = [
    "postedCompany_name",
    "positionLevels",
    "title",
    "numberOfVacancies",
    "employmentTypes",
    "minimumYearsExperience",
    "salary_maximum",
    "salary_minimum",
    "average_salary",
]
if show_job_post_id:
    table_column_order.append("metadata_jobPostId")

st.dataframe(
    filtered,
    #width="stretch", 
    use_container_width=True,
    hide_index=True,
    column_order=table_column_order,
    column_config={
        "postedCompany_name": st.column_config.TextColumn("Company"),
        "positionLevels": st.column_config.TextColumn("Position level"),
        "title": st.column_config.TextColumn("Title", width="large"),
        "numberOfVacancies": st.column_config.NumberColumn("Vacancies", format="%d"),
        "employmentTypes": st.column_config.TextColumn("Employment type"),
        "minimumYearsExperience": st.column_config.NumberColumn("Min. years experience", format="%d"),
        "salary_maximum": st.column_config.NumberColumn("Salary max", format="dollar"),
        "salary_minimum": st.column_config.NumberColumn("Salary min", format="dollar"),
        "average_salary": st.column_config.NumberColumn("Avg salary", format="dollar"),
        "metadata_jobPostId": st.column_config.TextColumn("Job Post ID"),
    },
)
