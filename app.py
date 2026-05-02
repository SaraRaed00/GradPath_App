"""
app.py
Main Streamlit application for GradPath AI.
Handles navigation and renders all pages.
"""

import streamlit as st
import pandas as pd
from datetime import date

from applications import (
    create_application,
    get_all_applications,
    update_application,
    delete_application,
    filter_applications,
    STATUS_OPTIONS,
    PRIORITY_OPTIONS,
    JOB_TYPE_OPTIONS,
    SOURCE_OPTIONS,
)
from analytics import (
    compute_metrics,
    get_upcoming_deadlines,
    chart_by_status,
    chart_over_time,
    chart_by_job_type,
    chart_by_source,
    chart_interview_rate_by_source,
    chart_upcoming_deadlines,
    generate_insights,
)
from ai_utils import analyze_job_description
from validation import validate_application
from sample_data import insert_one_sample_application


# Page config

st.set_page_config(
    page_title="GradPath AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Premium UI styling

st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(37,99,235,0.16), transparent 32%),
            radial-gradient(circle at bottom right, rgba(14,165,233,0.10), transparent 34%),
            linear-gradient(180deg, #070b14 0%, #0f172a 100%);
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        max-width: 1220px;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #060a13 0%, #0b1120 100%);
        border-right: 1px solid rgba(148,163,184,0.12);
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 750 !important;
        letter-spacing: -0.035em;
    }

    p, label, div {
        color: #cbd5e1;
    }

    hr {
        border-color: rgba(148,163,184,0.16);
    }

    /* Sidebar brand */
    .sidebar-brand {
        padding: 16px 15px;
        border: 1px solid rgba(148,163,184,0.14);
        border-radius: 18px;
        background:
            linear-gradient(180deg, rgba(30,41,59,0.78), rgba(15,23,42,0.78));
        box-shadow: 0 18px 30px rgba(0,0,0,0.28);
        margin-bottom: 1rem;
    }

    .sidebar-brand .logo {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, rgba(37,99,235,0.9), rgba(14,165,233,0.85));
        color: white;
        margin-bottom: 12px;
        box-shadow: 0 12px 24px rgba(37,99,235,0.35);
    }

    .sidebar-brand h2 {
        margin: 0;
        font-size: 1.15rem;
        letter-spacing: -0.02em;
    }

    .sidebar-brand p {
        margin: 6px 0 0 0;
        color: #94a3b8 !important;
        font-size: 0.82rem;
        line-height: 1.35;
    }

    .sidebar-footer {
        color: #64748b;
        font-size: 0.72rem;
        line-height: 1.5;
        border-top: 1px solid rgba(148,163,184,0.12);
        padding-top: 1rem;
        margin-top: 1rem;
    }

    /* Page header */
    .page-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 1.3rem;
    }

    .page-header-icon {
        width: 48px;
        height: 48px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, rgba(37,99,235,0.20), rgba(14,165,233,0.14));
        border: 1px solid rgba(96,165,250,0.25);
        color: #60a5fa;
        font-size: 1.05rem;
        box-shadow: 0 10px 22px rgba(0,0,0,0.18);
    }

    .page-header h1 {
        margin: 0;
        line-height: 1.05;
    }

    .page-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 6px;
    }

    /* Metric cards */
    [data-testid="stMetricContainer"],
    [data-testid="metric-container"] {
        background: linear-gradient(180deg, rgba(30,41,59,0.94), rgba(15,23,42,0.94));
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 14px 28px rgba(0,0,0,0.24);
    }

    [data-testid="stMetricLabel"],
    [data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.82rem !important;
        font-weight: 650 !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: 1.85rem !important;
        font-weight: 800 !important;
    }

    /* Forms and inputs */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select,
    .stDateInput input,
    div[data-baseweb="select"] > div {
        background: rgba(15, 23, 42, 0.92) !important;
        border: 1px solid rgba(148,163,184,0.22) !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
    }

    textarea {
        color: #f8fafc !important;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button,
    button[kind="primary"],
    button[kind="secondary"] {
        border-radius: 12px !important;
        font-weight: 650 !important;
        border: 1px solid rgba(96,165,250,0.22) !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.18);
    }

    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
        color: white !important;
        border-color: rgba(147,197,253,0.36) !important;
    }

    /* Tables and charts */
    .stDataFrame {
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 16px 32px rgba(0,0,0,0.20);
    }

    /* Alerts */
    .stAlert {
        border-radius: 14px !important;
        border: 1px solid rgba(148,163,184,0.14);
    }

    /* Cards */
    .pipeline-card {
        background: linear-gradient(180deg, rgba(30,41,59,0.94), rgba(15,23,42,0.94));
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 18px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 14px 26px rgba(0,0,0,0.20);
    }

    .pipeline-card .stage-icon {
        width: 44px;
        height: 44px;
        margin: 0 auto 10px auto;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(37,99,235,0.14);
        border: 1px solid rgba(96,165,250,0.18);
        color: #60a5fa;
        font-size: 1rem;
    }

    .pipeline-card .stage-name {
        color: #cbd5e1;
        font-weight: 650;
        margin-bottom: 4px;
    }

    .pipeline-card .stage-value {
        color: #f8fafc;
        font-size: 1.8rem;
        font-weight: 800;
    }

    .deadline-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(180deg, rgba(30,41,59,0.94), rgba(15,23,42,0.94));
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.65rem;
        border: 1px solid rgba(148,163,184,0.14);
        box-shadow: 0 10px 22px rgba(0,0,0,0.16);
    }

    .deadline-title {
        color: #f8fafc;
        font-weight: 650;
    }

    .deadline-subtitle {
        color: #94a3b8;
        font-size: 0.86rem;
        margin-top: 2px;
    }

    .deadline-badge {
        font-weight: 750;
        font-size: 0.85rem;
        padding: 0.35rem 0.6rem;
        border-radius: 999px;
    }

    .insight-card {
        background: linear-gradient(180deg, rgba(30,41,59,0.94), rgba(15,23,42,0.94));
        border: 1px solid rgba(148,163,184,0.16);
        border-left: 4px solid #3b82f6;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 12px 24px rgba(0,0,0,0.18);
    }

    .insight-title {
        color: #f8fafc;
        font-weight: 750;
        margin-bottom: 4px;
    }

    .insight-body {
        color: #94a3b8;
        line-height: 1.5;
    }

    .subtle-card {
        background: linear-gradient(180deg, rgba(30,41,59,0.74), rgba(15,23,42,0.74));
        border: 1px solid rgba(148,163,184,0.14);
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .small-muted {
        color: #94a3b8;
        font-size: 0.85rem;
        line-height: 1.45;
    }

    .feature-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border: 1px solid rgba(96,165,250,0.22);
        background: rgba(37,99,235,0.10);
        color: #bfdbfe;
        border-radius: 999px;
        padding: 0.38rem 0.7rem;
        font-size: 0.82rem;
        font-weight: 650;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Helper functions

def render_page_header(icon_class: str, title: str, subtitle: str) -> None:
    """Render a consistent premium page header."""
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-header-icon"><i class="{icon_class}"></i></div>
            <div>
                <h1>{title}</h1>
                <div class="page-subtitle">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    """Render sidebar brand block."""
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="logo"><i class="fa-solid fa-graduation-cap"></i></div>
            <h2>GradPath AI</h2>
            <p>Career tracking for students and fresh graduates.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_option_index(options: list[str], value: str | None, default_index: int = 0) -> int:
    """Return the index of value in options, with a safe fallback."""
    if value in options:
        return options.index(value)
    return default_index


# Sidebar navigation

with st.sidebar:
    render_sidebar_brand()

    page = st.radio(
        "Navigate",
        options=[
            "Dashboard",
            "Add Application",
            "Applications",
            "Analytics",
            "AI Assistant",
            "About",
        ],
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div class="sidebar-footer">
            GradPath AI v1.0<br>
            Built with Streamlit, Supabase, pandas, Plotly, and AI-supported guidance.
        </div>
        """,
        unsafe_allow_html=True,
    )

# PAGE: Dashboard
if page == "Dashboard":
    render_page_header(
        "fa-solid fa-chart-line",
        "Dashboard",
        "A high-level view of your job search pipeline, deadlines, and progress.",
    )

    df = get_all_applications()
    metrics = compute_metrics(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Applications", metrics["total"])
    c2.metric("Active", metrics["active"])
    c3.metric("Interviews", metrics["interviews"])
    c4.metric("Offers", metrics["offers"])
    c5.metric("Rejections", metrics["rejections"])

    c6, c7, c8 = st.columns(3)
    c6.metric("Interview Rate", f"{metrics['interview_rate']}%")
    c7.metric("Offer Rate", f"{metrics['offer_rate']}%")
    c8.metric("Deadlines in 7 Days", metrics["upcoming_deadlines"])

    st.divider()

    st.subheader("Application Pipeline")

    cols = st.columns(5)
    stages = [
        ("fa-regular fa-bookmark", "Saved"),
        ("fa-solid fa-paper-plane", "Applied"),
        ("fa-regular fa-comments", "Interview"),
        ("fa-solid fa-circle-check", "Offer"),
        ("fa-solid fa-circle-xmark", "Rejected"),
    ]

    status_counts = df["status"].value_counts() if not df.empty else {}

    for col, (icon, stage) in zip(cols, stages):
        count = (
            int(status_counts.get(stage, 0))
            if not isinstance(status_counts, dict)
            else status_counts.get(stage, 0)
        )

        with col:
            st.markdown(
                f"""
                <div class="pipeline-card">
                    <div class="stage-icon"><i class="{icon}"></i></div>
                    <div class="stage-name">{stage}</div>
                    <div class="stage-value">{count}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    st.subheader("Upcoming Deadlines")
    st.caption("Applications with deadlines in the next 7 days.")

    upcoming = get_upcoming_deadlines(df, days=7)

    if upcoming.empty:
        st.info("No deadlines in the next 7 days.")
    else:
        for _, row in upcoming.iterrows():
            days_left = int(row["days_left"])

            if days_left <= 2:
                badge_bg = "rgba(248,113,113,0.14)"
                badge_color = "#fca5a5"
                border_color = "#f87171"
            elif days_left <= 4:
                badge_bg = "rgba(245,158,11,0.14)"
                badge_color = "#fbbf24"
                border_color = "#f59e0b"
            else:
                badge_bg = "rgba(52,211,153,0.14)"
                badge_color = "#6ee7b7"
                border_color = "#34d399"

            st.markdown(
                f"""
                <div class="deadline-card" style="border-left:4px solid {border_color};">
                    <div>
                        <div class="deadline-title">{row['company']} — {row['job_title']}</div>
                        <div class="deadline-subtitle">Status: {row.get('status', 'N/A')}</div>                    </div>
                    <div class="deadline-badge" style="background:{badge_bg}; color:{badge_color};">
                        {days_left} days left
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )



# PAGE: Add Application

elif page == "Add Application":
    render_page_header(
        "fa-solid fa-briefcase",
        "Add Application",
        "Store a new opportunity with structured details and a job description for analysis.",
    )

    with st.expander("Demo helper", expanded=False):
        st.markdown(
            """
            <div class="small-muted">
            Use this only for presentation setup. It inserts one realistic sample application
            and avoids creating duplicates.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Insert 1 sample application", width="stretch"):
            with st.spinner("Adding one sample application..."):
                success, message = insert_one_sample_application()

            if success:
                st.success(message)
                st.rerun()
            else:
                st.info(message)

    with st.form("add_application_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            company = st.text_input("Company *", placeholder="Example: EdTech Kuwait")
            job_title = st.text_input("Job Title *", placeholder="Example: Junior Data Analyst Intern")
            job_type = st.selectbox("Job Type *", JOB_TYPE_OPTIONS)
            location = st.text_input("Location", placeholder="Example: Kuwait City, Kuwait")
            application_date = st.date_input("Application Date *", value=date.today())
            deadline = st.date_input("Deadline", value=None)

        with col2:
            status = st.selectbox("Status *", STATUS_OPTIONS, index=1)
            priority = st.selectbox("Priority *", PRIORITY_OPTIONS, index=1)
            source = st.selectbox("Source", SOURCE_OPTIONS)
            notes = st.text_area(
                "Notes",
                placeholder="Add personal notes, follow-up reminders, or preparation points.",
                max_chars=500,
                height=120,
            )

        job_description = st.text_area(
            "Job Description",
            placeholder="Paste the full job description here. The AI Assistant can analyze it later.",
            max_chars=4000,
            height=210,
        )

        submitted = st.form_submit_button("Save Application", width="stretch")

    if submitted:
        errors = validate_application(
            company=company,
            job_title=job_title,
            job_type=job_type,
            application_date=application_date,
            status=status,
            priority=priority,
            deadline=deadline,
            notes=notes,
            job_description=job_description,
        )

        if errors:
            for err in errors:
                st.error(err)
        else:
            payload = {
                "company": company.strip(),
                "job_title": job_title.strip(),
                "job_type": job_type,
                "location": location.strip() or None,
                "application_date": application_date,
                "deadline": deadline,
                "status": status,
                "priority": priority,
                "source": source,
                "job_description": job_description.strip() or None,
                "notes": notes.strip() or None,
            }

            result = create_application(payload)

            if result:
                st.success(f"Application to {company} saved successfully.")

                if not job_description.strip():
                    st.info(
                        "Tip: add a job description later or paste one in the AI Assistant "
                        "to generate preparation guidance."
                    )
            else:
                st.error(
                    "Something went wrong while saving the application. "
                    "Check the Supabase connection and table policies."
                )


# PAGE: Applications

elif page == "Applications":
    render_page_header(
        "fa-solid fa-table-list",
        "Applications",
        "Search, filter, sort, update, and manage your saved opportunities.",
    )

    col_refresh, col_spacer = st.columns([1, 5])

    with col_refresh:
        if st.button("Refresh", width="stretch"):
            st.cache_resource.clear()
            st.rerun()

    df = get_all_applications()

    if df.empty:
        st.info("No applications found. Add your first application to begin.")
        st.stop()

    with st.expander("Search and Filter", expanded=True):
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)

        with fcol1:
            search_q = st.text_input("Search", placeholder="Company, title, or source")

        with fcol2:
            status_filter = st.multiselect("Status", STATUS_OPTIONS)

        with fcol3:
            type_filter = st.multiselect("Job Type", JOB_TYPE_OPTIONS)

        with fcol4:
            priority_filter = st.multiselect("Priority", PRIORITY_OPTIONS)

        scol1, scol2 = st.columns(2)

        with scol1:
            sort_by = st.selectbox(
                "Sort By",
                ["application_date", "deadline", "status", "priority", "company"],
                format_func=lambda x: x.replace("_", " ").title(),
            )

        with scol2:
            sort_order = st.radio(
                "Order",
                ["Newest First", "Oldest First"],
                horizontal=True,
            )

    filtered = filter_applications(
        df,
        search_query=search_q,
        status_filter=status_filter or None,
        job_type_filter=type_filter or None,
        priority_filter=priority_filter or None,
        sort_by=sort_by,
        sort_asc=(sort_order == "Oldest First"),
    )

    st.markdown(f"**{len(filtered)}** application(s) found.")

    if filtered.empty:
        st.warning("No applications match the selected filters.")
        st.stop()

    display_cols = [
        "company",
        "job_title",
        "job_type",
        "status",
        "priority",
        "application_date",
        "deadline",
        "source",
    ]

    available = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[available].rename(
            columns={c: c.replace("_", " ").title() for c in available}
        ),
        width="stretch",
        hide_index=True,
    )

    st.divider()

    st.subheader("Edit or Delete an Application")

    app_options = {
        f"{row['company']} — {row['job_title']} (#{row['id']})": row["id"]
        for _, row in filtered.iterrows()
    }

    selected_label = st.selectbox("Select application", list(app_options.keys()))
    selected_id = app_options[selected_label]
    selected_row = filtered[filtered["id"] == selected_id].iloc[0]

    edit_tab, delete_tab = st.tabs(["Edit", "Delete"])

    with edit_tab:
        with st.form(f"edit_form_{selected_id}"):
            ec1, ec2 = st.columns(2)

            with ec1:
                e_company = st.text_input(
                    "Company *",
                    value=selected_row.get("company", ""),
                )
                e_title = st.text_input(
                    "Job Title *",
                    value=selected_row.get("job_title", ""),
                )
                e_type = st.selectbox(
                    "Job Type *",
                    JOB_TYPE_OPTIONS,
                    index=safe_option_index(
                        JOB_TYPE_OPTIONS,
                        selected_row.get("job_type"),
                    ),
                )
                e_location = st.text_input(
                    "Location",
                    value=selected_row.get("location") or "",
                )
                e_app_date = st.date_input(
                    "Application Date *",
                    value=pd.Timestamp(selected_row["application_date"]).date(),
                )
                e_deadline = st.date_input(
                    "Deadline",
                    value=(
                        pd.Timestamp(selected_row["deadline"]).date()
                        if pd.notna(selected_row.get("deadline"))
                        else None
                    ),
                )

            with ec2:
                e_status = st.selectbox(
                    "Status *",
                    STATUS_OPTIONS,
                    index=safe_option_index(
                        STATUS_OPTIONS,
                        selected_row.get("status"),
                    ),
                )
                e_priority = st.selectbox(
                    "Priority *",
                    PRIORITY_OPTIONS,
                    index=safe_option_index(
                        PRIORITY_OPTIONS,
                        selected_row.get("priority"),
                    ),
                )
                e_source = st.selectbox(
                    "Source",
                    SOURCE_OPTIONS,
                    index=safe_option_index(
                        SOURCE_OPTIONS,
                        selected_row.get("source"),
                    ),
                )
                e_notes = st.text_area(
                    "Notes",
                    value=selected_row.get("notes") or "",
                    max_chars=500,
                )

            e_jd = st.text_area(
                "Job Description",
                value=selected_row.get("job_description") or "",
                max_chars=4000,
                height=130,
            )

            save_edit = st.form_submit_button("Save Changes", width="stretch")

        if save_edit:
            errors = validate_application(
                company=e_company,
                job_title=e_title,
                job_type=e_type,
                application_date=e_app_date,
                status=e_status,
                priority=e_priority,
                deadline=e_deadline,
                notes=e_notes,
                job_description=e_jd,
            )

            if errors:
                for err in errors:
                    st.error(err)
            else:
                ok = update_application(
                    selected_id,
                    {
                        "company": e_company.strip(),
                        "job_title": e_title.strip(),
                        "job_type": e_type,
                        "location": e_location.strip() or None,
                        "application_date": e_app_date,
                        "deadline": e_deadline,
                        "status": e_status,
                        "priority": e_priority,
                        "source": e_source,
                        "notes": e_notes.strip() or None,
                        "job_description": e_jd.strip() or None,
                    },
                )

                if ok:
                    st.success("Application updated.")
                    st.rerun()

    with delete_tab:
        st.warning(
            f"Are you sure you want to delete "
            f"{selected_row['company']} — {selected_row['job_title']}? "
            "This action cannot be undone."
        )

        if st.button("Delete Application", type="primary"):
            ok = delete_application(selected_id)

            if ok:
                st.success("Application deleted.")
                st.rerun()


# PAGE: Analytics

elif page == "Analytics":
    render_page_header(
        "fa-solid fa-chart-pie",
        "Analytics",
        "Interactive data analysis for application trends, sources, and deadlines.",
    )

    st.markdown(
        """
        <div class="feature-pill">
            <i class="fa-solid fa-database"></i>
            Data Science Feature
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = get_all_applications()

    if df.empty:
        st.info("No data available yet. Add applications or use the demo helper.")
        st.stop()

    st.subheader("Smart Insights")
    insights = generate_insights(df)

    for ins in insights:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">{ins['title']}</div>
                <div class="insight-body">{ins['body']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.plotly_chart(chart_by_status(df), width="stretch")

    with c2:
        st.plotly_chart(chart_over_time(df), width="stretch")

    c3, c4 = st.columns(2)

    with c3:
        st.plotly_chart(chart_by_job_type(df), width="stretch")

    with c4:
        st.plotly_chart(chart_by_source(df), width="stretch")

    c5, c6 = st.columns(2)

    with c5:
        st.plotly_chart(chart_interview_rate_by_source(df), width="stretch")

    with c6:
        st.plotly_chart(chart_upcoming_deadlines(df, days=30), width="stretch")

    st.divider()

    with st.expander("View Status Summary Table"):
        summary = (
            df.groupby("status")
            .agg(
                Count=("id", "count"),
            )
            .reset_index()
        )

        st.dataframe(summary, width="stretch", hide_index=True)


# PAGE: AI Assistant

elif page == "AI Assistant":
    render_page_header(
        "fa-solid fa-sparkles",
        "AI Job Preparation Assistant",
        "Analyze job descriptions and generate preparation guidance for students.",
    )

    st.markdown(
        """
        <div class="feature-pill">
            <i class="fa-solid fa-wand-magic-sparkles"></i>
            AI Bonus Feature
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Responsible AI Notice: suggestions are generated automatically and may not be fully accurate. "
        "Review and personalize them before using them in real applications or interviews."
    )

    df = get_all_applications()

    mode = st.radio(
        "Choose input method:",
        ["Select an existing application", "Paste a job description manually"],
        horizontal=True,
    )

    company, job_title, job_description = "", "", ""

    if mode == "Select an existing application":
        if df.empty:
            st.warning("No applications found. Add one first, or switch to manual mode.")
            st.stop()

        options = {
            f"{r['company']} — {r['job_title']} (#{r['id']})": i
            for i, r in df.iterrows()
        }

        chosen_label = st.selectbox("Select application", list(options.keys()))
        chosen_row = df.loc[options[chosen_label]]

        company = chosen_row.get("company", "") or ""
        job_title = chosen_row.get("job_title", "") or ""
        saved_description = chosen_row.get("job_description", "")

        if pd.isna(saved_description):
            saved_description = ""

        if saved_description.strip():
            job_description = saved_description

            with st.expander("Preview Job Description"):
                st.text(
                    job_description[:1000]
                    + ("..." if len(job_description) > 1000 else "")
                )
        else:
            st.warning(
                "This application does not have a saved job description. "
                "Paste one below to analyze it."
            )

            job_description = st.text_area(
                "Job Description *",
                placeholder="Paste the job description for this application.",
                height=250,
                max_chars=4000,
            )

    else:
        company = st.text_input("Company", placeholder="Example: EdTech Kuwait")
        job_title = st.text_input("Job Title", placeholder="Example: Junior Data Analyst Intern")
        job_description = st.text_area(
            "Job Description *",
            placeholder="Paste the full job description here.",
            height=250,
            max_chars=4000,
        )

    if st.button("Analyze Job Description", type="primary", width="stretch"):
        if not job_description or len(job_description.strip()) < 30:
            st.error("Please provide a job description with at least 30 characters.")
        else:
            with st.spinner("Analyzing the job description..."):
                result = analyze_job_description(job_description, company, job_title)

            if result["source"] == "openai":
                st.success("Analysis generated using OpenAI GPT.")
            elif result["source"] == "fallback":
                st.warning(
                    "OpenAI API key is not configured. Showing rule-based analysis instead."
                )
            elif result["source"] == "error":
                st.error(result["content"])

            if result["source"] != "error":
                st.divider()
                st.markdown(result["content"])

                st.divider()
                st.download_button(
                    "Download Analysis",
                    data=result["content"],
                    file_name=f"gradpath_analysis_{company or 'job'}.md".replace(" ", "_"),
                    mime="text/markdown",
                    width="stretch",
                )


# PAGE: About

elif page == "About":
    render_page_header(
        "fa-solid fa-circle-info",
        "About GradPath AI",
        "Project overview, architecture, and implementation summary.",
    )

    st.markdown(
        """
## What is GradPath AI?

**GradPath AI** is a job application tracker built specifically for university students and fresh graduates. It helps users organize applications, track progress through the hiring pipeline, analyze job search trends, and prepare for interviews using AI-supported guidance.

---

## Why was it built?

Students applying to internships, graduate programs, and entry-level jobs often have information scattered across emails, spreadsheets, job boards, and LinkedIn bookmarks. GradPath AI gives students one clean, centralized place to manage their job search.

---

## Target Users

- Final-year university students
- Fresh graduates entering the job market
- Internship seekers
- Students applying to graduate programs
- University career center users

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend / App | Streamlit |
| Language | Python |
| Database | Supabase PostgreSQL |
| Data Analysis | pandas |
| Charts | Plotly |
| AI Feature | OpenAI GPT-4o-mini with rule-based fallback |
| Config | python-dotenv / Streamlit secrets |

---

## Database Choice

**Supabase** was chosen because it provides a hosted PostgreSQL database with a simple Python client. This makes the app easier to deploy than a local-only database while still demonstrating real database storage, retrieval, update, and deletion.

---

AI Feature: Job Preparation Assistant

The **AI Job Preparation Assistant** analyzes job descriptions and returns:

- A plain-language job summary
- Key required skills
- Resume keywords
- Interview preparation topics
- A follow-up email draft
- Practical next steps

Since i didnot include a key,, im using a rule-based fallback analyzer that detects common keywords across 
technical, business, marketing, finance, education, healthcare, design, HR, legal, and soft-skill categories.


When an OpenAI API key is configured, the app uses OpenAI's `gpt-4o-mini` model. If no API key is configured, the app uses 
a rule-based fallback analyzer that detects common keywords across technical, business, marketing, finance, education, healthcare, design, HR, legal, and soft-skill categories.


## Data Science Feature: Analytics Dashboard

The **Analytics page** is the data science bonus feature. It uses `pandas` for data transformation and `Plotly` for interactive charts.

It includes:
- Applications by status
- Applications submitted over time
- Applications by job type
- Applications by source
- Interview rate by source
- Upcoming deadlines timeline
- Smart text insights based on job search data


## Project Structure

```text
gradpath_ai/
├── app.py           # Main Streamlit app, navigation, all pages
├── database.py      # Supabase client setup
├── applications.py  # CRUD + search/filter/sort logic
├── analytics.py     # Metrics, Plotly charts, smart insights
├── ai_utils.py      # AI job description analyzer + fallback
├── validation.py    # Form validation and error messages
├── sample_data.py   # Demo helper for inserting sample data
├── requirements.txt
├── README.md
└── .env.example 

Tasks completed without AI assistance
Database schema design and Supabase setup
Form validation logic
Filter and sort logic for applications
Smart insight generation rules
Rule-based fallback analyzer
Page layout and navigation structure
README and documentation

""")