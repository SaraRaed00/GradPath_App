"""
analytics.py
Dashboard metrics, Plotly charts, and smart insights using pandas.
This module is the data science bonus feature of GradPath AI.
"""

from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ── Colour palette (consistent across all charts) ─────────────────────────────

COLORS = {
    "Saved": "#94a3b8",
    "Applied": "#60a5fa",
    "Interview": "#f59e0b",
    "Offer": "#34d399",
    "Rejected": "#f87171",
    "Low": "#94a3b8",
    "Medium": "#60a5fa",
    "High": "#f87171",
}

CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono, monospace", color="#e2e8f0"),
    margin=dict(l=20, r=20, t=40, b=20),
)


# ── Summary metrics ────────────────────────────────────────────────────────────

def compute_metrics(df: pd.DataFrame) -> dict:
    """
    Compute summary KPIs for the dashboard.
    Returns a dict of metric name → value.
    """
    if df.empty:
        return {
            "total": 0,
            "active": 0,
            "interviews": 0,
            "offers": 0,
            "rejections": 0,
            "upcoming_deadlines": 0,
            "interview_rate": 0.0,
            "offer_rate": 0.0,
        }

    total = len(df)
    status_counts = df["status"].value_counts()

    interviews = int(status_counts.get("Interview", 0))
    offers = int(status_counts.get("Offer", 0))
    rejections = int(status_counts.get("Rejected", 0))
    saved = int(status_counts.get("Saved", 0))
    applied = int(status_counts.get("Applied", 0))
    active = saved + applied + interviews

    # Applications that progressed past Applied
    applied_or_more = total - saved
    interview_rate = (interviews + offers) / applied_or_more * 100 if applied_or_more else 0.0
    offer_rate = offers / applied_or_more * 100 if applied_or_more else 0.0

    # Upcoming deadlines within 7 days
    today = pd.Timestamp(date.today())
    week_later = today + pd.Timedelta(days=7)
    if "deadline" in df.columns:
        upcoming = df[
            df["deadline"].notna()
            & (df["deadline"] >= today)
            & (df["deadline"] <= week_later)
            & (~df["status"].isin(["Offer", "Rejected"]))
        ]
        upcoming_count = len(upcoming)
    else:
        upcoming_count = 0

    return {
        "total": total,
        "active": active,
        "interviews": interviews,
        "offers": offers,
        "rejections": rejections,
        "upcoming_deadlines": upcoming_count,
        "interview_rate": round(interview_rate, 1),
        "offer_rate": round(offer_rate, 1),
    }


def get_upcoming_deadlines(df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    """Return applications with deadlines in the next `days` days."""
    if df.empty or "deadline" not in df.columns:
        return pd.DataFrame()

    today = pd.Timestamp(date.today())
    cutoff = today + pd.Timedelta(days=days)

    upcoming = df[
        df["deadline"].notna()
        & (df["deadline"] >= today)
        & (df["deadline"] <= cutoff)
        & (~df["status"].isin(["Offer", "Rejected"]))
    ].copy()

    if upcoming.empty:
        return upcoming

    upcoming["days_left"] = (upcoming["deadline"] - today).dt.days
    return upcoming.sort_values("days_left")[
        ["company", "job_title", "status", "deadline", "days_left"]
    ]


# ── Plotly charts ──────────────────────────────────────────────────────────────

def chart_by_status(df: pd.DataFrame) -> go.Figure:
    """Donut chart of applications grouped by status."""
    counts = df["status"].value_counts().reset_index()
    counts.columns = ["status", "count"]
    colors = [COLORS.get(s, "#94a3b8") for s in counts["status"]]

    fig = go.Figure(
        go.Pie(
            labels=counts["status"],
            values=counts["count"],
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#1e293b", width=2)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>%{value} applications<extra></extra>",
        )
    )
    fig.update_layout(
        title="Applications by Status",
        showlegend=False,
        **CHART_THEME,
    )
    return fig


def chart_over_time(df: pd.DataFrame) -> go.Figure:
    """Line chart of applications submitted over time (weekly buckets)."""
    if "application_date" not in df.columns or df["application_date"].isna().all():
        return _empty_chart("Applications Over Time")

    timeline = (
        df.dropna(subset=["application_date"])
        .assign(week=lambda d: d["application_date"].dt.to_period("W").apply(lambda p: p.start_time))
        .groupby("week")
        .size()
        .reset_index(name="count")
    )

    fig = px.line(
        timeline,
        x="week",
        y="count",
        markers=True,
        labels={"week": "Week", "count": "Applications"},
        title="Applications Submitted Over Time",
    )
    fig.update_traces(
        line=dict(color="#60a5fa", width=2.5),
        marker=dict(color="#f59e0b", size=8),
    )
    fig.update_layout(**CHART_THEME)
    return fig


def chart_by_job_type(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of applications by job type."""
    counts = df["job_type"].value_counts().reset_index()
    counts.columns = ["job_type", "count"]

    fig = px.bar(
        counts,
        x="count",
        y="job_type",
        orientation="h",
        labels={"count": "Applications", "job_type": "Job Type"},
        title="Applications by Job Type",
        color="count",
        color_continuous_scale=["#1e3a5f", "#60a5fa"],
    )
    fig.update_layout(coloraxis_showscale=False, **CHART_THEME)
    return fig


def chart_by_source(df: pd.DataFrame) -> go.Figure:
    """Bar chart of applications by source."""
    counts = df["source"].value_counts().reset_index()
    counts.columns = ["source", "count"]

    fig = px.bar(
        counts,
        x="source",
        y="count",
        labels={"count": "Applications", "source": "Source"},
        title="Applications by Source",
        color="count",
        color_continuous_scale=["#1e3a5f", "#34d399"],
    )
    fig.update_layout(coloraxis_showscale=False, **CHART_THEME)
    return fig


def chart_interview_rate_by_source(df: pd.DataFrame) -> go.Figure:
    """
    Bar chart: interview rate (%) per source.
    Interview rate = (Interview + Offer) / total applications from that source.
    """
    if df.empty:
        return _empty_chart("Interview Rate by Source")

    summary = (
        df.groupby("source")
        .apply(
            lambda g: pd.Series(
                {
                    "total": len(g),
                    "interviews": (g["status"].isin(["Interview", "Offer"])).sum(),
                }
            )
        )
        .reset_index()
    )
    summary["rate"] = summary["interviews"] / summary["total"] * 100
    summary = summary[summary["total"] >= 1].sort_values("rate", ascending=False)

    fig = px.bar(
        summary,
        x="source",
        y="rate",
        labels={"rate": "Interview Rate (%)", "source": "Source"},
        title="Interview Rate by Source",
        color="rate",
        color_continuous_scale=["#1e3a5f", "#f59e0b"],
    )
    fig.update_layout(coloraxis_showscale=False, **CHART_THEME)
    return fig


def chart_upcoming_deadlines(df: pd.DataFrame, days: int = 30) -> go.Figure:
    """Timeline scatter of upcoming deadlines."""
    if "deadline" not in df.columns:
        return _empty_chart("Upcoming Deadlines")

    today = pd.Timestamp(date.today())
    cutoff = today + pd.Timedelta(days=days)

    upcoming = df[
        df["deadline"].notna()
        & (df["deadline"] >= today)
        & (df["deadline"] <= cutoff)
    ].copy()

    if upcoming.empty:
        return _empty_chart("Upcoming Deadlines (none in next 30 days)")

    upcoming["label"] = upcoming["company"] + " — " + upcoming["job_title"]
    colors = [COLORS.get(s, "#94a3b8") for s in upcoming["status"]]

    fig = go.Figure(
        go.Scatter(
            x=upcoming["deadline"],
            y=upcoming["label"],
            mode="markers",
            marker=dict(color=colors, size=14, symbol="diamond"),
            hovertemplate="<b>%{y}</b><br>Deadline: %{x|%b %d, %Y}<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"Upcoming Deadlines (next {days} days)",
        xaxis_title="Deadline",
        yaxis_title="",
        **CHART_THEME,
    )
    return fig


# ── Smart insights ─────────────────────────────────────────────────────────────

def generate_insights(df: pd.DataFrame) -> list[dict]:
    """
    Generate a list of plain-language insight strings from the dataset.
    Each insight is a dict with 'icon', 'title', and 'body'.
    """
    insights = []
    if df.empty:
        return [{"icon": "💡", "title": "No data yet", "body": "Add your first application to start seeing insights."}]

    # Best source by interview rate
    summary = (
        df.groupby("source")
        .apply(lambda g: pd.Series({"total": len(g), "interviews": (g["status"].isin(["Interview", "Offer"])).sum()}))
        .reset_index()
    )
    summary["rate"] = summary["interviews"] / summary["total"]
    best = summary[summary["total"] >= 2].sort_values("rate", ascending=False)
    if not best.empty:
        top_source = best.iloc[0]
        insights.append({
            "icon": "🏆",
            "title": "Best Source",
            "body": f"{top_source['source']} gives you the highest interview rate ({top_source['rate']*100:.0f}%) with {int(top_source['total'])} applications.",
        })

    # High-priority apps due soon
    today = pd.Timestamp(date.today())
    if "deadline" in df.columns:
        soon = df[
            df["deadline"].notna()
            & (df["deadline"] >= today)
            & (df["deadline"] <= today + pd.Timedelta(days=7))
            & (df["priority"] == "High")
            & (~df["status"].isin(["Offer", "Rejected"]))
        ]
        if not soon.empty:
            insights.append({
                "icon": "🔥",
                "title": "Urgent Deadlines",
                "body": f"You have {len(soon)} high-priority application(s) due within the next 7 days.",
            })

    # Most common status
    top_status = df["status"].value_counts().idxmax()
    top_count = df["status"].value_counts().max()
    insights.append({
        "icon": "📊",
        "title": "Most Common Status",
        "body": f"{top_count} of your applications are currently in '{top_status}' status.",
    })

    # Recent activity (last 14 days)
    if "application_date" in df.columns:
        recent = df[df["application_date"] >= today - pd.Timedelta(days=14)]
        insights.append({
            "icon": "📅",
            "title": "Recent Activity",
            "body": f"You submitted {len(recent)} application(s) in the last 14 days.",
        })

    # No-response rate
    applied_df = df[df["status"] == "Applied"]
    if len(applied_df) > 0:
        old = applied_df[
            applied_df["application_date"] <= today - pd.Timedelta(days=21)
        ] if "application_date" in df.columns else pd.DataFrame()
        if not old.empty:
            insights.append({
                "icon": "⏳",
                "title": "Awaiting Response",
                "body": f"{len(old)} application(s) marked 'Applied' have received no update in over 3 weeks. Consider following up.",
            })

    return insights


# ── Helpers ────────────────────────────────────────────────────────────────────

def _empty_chart(title: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=title,
        annotations=[dict(text="No data available", showarrow=False, font=dict(color="#94a3b8", size=14))],
        **CHART_THEME,
    )
    return fig