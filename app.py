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


# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="GradPath AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Global CSS ─────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* Import IBM Plex Mono for that clean, technical feel */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Dark sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem;
    }
    [data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.75rem !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 2rem !important;
    }

    /* Main background */
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }

    /* Headings */
    h1, h2, h3 {
        color: #f1f5f9 !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* Buttons */
    .stButton > button {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background: #2563eb;
    }

    /* Input fields */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Info/success/warning/error boxes */
    .stAlert {
        border-radius: 10px;
    }

    /* Dividers */
    hr {
        border-color: #334155;
    }

    /* Pipeline boxes */
    .pipeline-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }

    /* Insight cards */
    .insight-card {
        background: #1e293b;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Sidebar navigation ─────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎓 GradPath AI")
    st.markdown("*Your job search command center*")
    st.divider()

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

    st.divider()
    st.markdown(
        "<span style='font-size:0.7rem;color:#475569;font-family:IBM Plex Mono,monospace'>"
        "GradPath AI v1.0<br>Built for students 🎓"
        "</span>",
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ════════════════════════════════════════════════════════════════════════════════

if page == "Dashboard":
    st.title("📊 Dashboard")
    st.caption("Your job search at a glance.")

    df = get_all_applications()
    metrics = compute_metrics(df)

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Applications", metrics["total"])
    c2.metric("Active", metrics["active"])
    c3.metric("Interviews", metrics["interviews"])
    c4.metric("Offers 🎉", metrics["offers"])
    c5.metric("Rejections", metrics["rejections"])

    c6, c7, c8 = st.columns(3)
    c6.metric("Interview Rate", f"{metrics['interview_rate']}%")
    c7.metric("Offer Rate", f"{metrics['offer_rate']}%")
    c8.metric("⏰ Deadlines (7 days)", metrics["upcoming_deadlines"])

    st.divider()

    # Pipeline
    st.subheader("Application Pipeline")

    cols = st.columns(5)
    stages = [
        ("💾", "Saved"),
        ("📤", "Applied"),
        ("🗣️", "Interview"),
        ("✅", "Offer"),
        ("❌", "Rejected"),
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
                <div class="pipeline-box">
                    <div style="font-size:1.75rem">{icon}</div>
                    <div style="font-weight:600;color:#e2e8f0">{stage}</div>
                    <div style="font-size:2rem;font-family:'IBM Plex Mono',monospace;color:#60a5fa">{count}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # Upcoming deadlines
    st.subheader("⏰ Upcoming Deadlines (Next 7 Days)")
    upcoming = get_upcoming_deadlines(df, days=7)

    if upcoming.empty:
        st.info("No deadlines in the next 7 days. You're on top of things! 🎉")
    else:
        for _, row in upcoming.iterrows():
            days_left = int(row["days_left"])
            color = (
                "#f87171"
                if days_left <= 2
                else "#f59e0b"
                if days_left <= 4
                else "#34d399"
            )

            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                    background:#1e293b;border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.5rem;
                    border-left:4px solid {color}">
                    <span><b>{row['company']}</b> — {row['job_title']}</span>
                    <span style="font-family:'IBM Plex Mono',monospace;color:{color}">{days_left}d left</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: Add Application
# ════════════════════════════════════════════════════════════════════════════════

elif page == "Add Application":
    st.title("➕ Add Application")
    st.caption("Track a new job, internship, or program.")

    # Demo helper: hidden by default, not shown globally in sidebar.
    with st.expander("Demo helper", expanded=False):
        st.caption(
            "Use this only during testing or presentation setup. "
            "It inserts one realistic sample application without creating duplicates."
        )

        if st.button("Insert 1 sample application", use_container_width=True):
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
            company = st.text_input("Company *", placeholder="e.g. Google")
            job_title = st.text_input("Job Title *", placeholder="e.g. Software Engineer Intern")
            job_type = st.selectbox("Job Type *", JOB_TYPE_OPTIONS)
            location = st.text_input("Location", placeholder="e.g. Dubai, UAE")
            application_date = st.date_input("Application Date *", value=date.today())
            deadline = st.date_input("Deadline", value=None)

        with col2:
            status = st.selectbox("Status *", STATUS_OPTIONS, index=1)
            priority = st.selectbox("Priority *", PRIORITY_OPTIONS, index=1)
            source = st.selectbox("Source", SOURCE_OPTIONS)
            notes = st.text_area(
                "Notes",
                placeholder="Any personal notes…",
                max_chars=500,
                height=120,
            )

        job_description = st.text_area(
            "Job Description",
            placeholder="Paste the full job description here (used by AI Assistant)…",
            max_chars=4000,
            height=200,
        )

        submitted = st.form_submit_button("💾 Save Application", use_container_width=True)

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
                st.error(f"❌ {err}")
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
                st.success(f"✅ Application to **{company}** saved successfully!")

                if not job_description.strip():
                    st.info(
                        "Tip: Add a job description later or paste one in the AI Assistant "
                        "if you want preparation suggestions for this application."
                    )
            else:
                st.error(
                    "Something went wrong saving your application. "
                    "Check your Supabase connection."
                )


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: Applications
# ════════════════════════════════════════════════════════════════════════════════

elif page == "Applications":
    st.title("📋 Applications")
    st.caption("Search, filter, and manage all your applications.")

    col_refresh, col_spacer = st.columns([1, 5])

    with col_refresh:
        if st.button("🔄 Refresh"):
            st.cache_resource.clear()
            st.rerun()

    df = get_all_applications()

    if df.empty:
        st.info("No applications yet. Add your first one! 🚀")
        st.stop()

    # Filters
    with st.expander("🔍 Search & Filter", expanded=True):
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)

        with fcol1:
            search_q = st.text_input("Search", placeholder="Company, title, or source…")

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
        st.warning("No applications match your filters.")
        st.stop()

    # Display table columns
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
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # Edit / Delete
    st.subheader("Edit or Delete an Application")

    app_options = {
        f"{row['company']} — {row['job_title']} (#{row['id']})": row["id"]
        for _, row in filtered.iterrows()
    }

    selected_label = st.selectbox("Select application", list(app_options.keys()))
    selected_id = app_options[selected_label]
    selected_row = filtered[filtered["id"] == selected_id].iloc[0]

    edit_tab, delete_tab = st.tabs(["✏️ Edit", "🗑️ Delete"])

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
                    index=JOB_TYPE_OPTIONS.index(
                        selected_row.get("job_type", JOB_TYPE_OPTIONS[0])
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
                    index=STATUS_OPTIONS.index(
                        selected_row.get("status", STATUS_OPTIONS[0])
                    ),
                )
                e_priority = st.selectbox(
                    "Priority *",
                    PRIORITY_OPTIONS,
                    index=PRIORITY_OPTIONS.index(
                        selected_row.get("priority", PRIORITY_OPTIONS[0])
                    ),
                )
                e_source = st.selectbox(
                    "Source",
                    SOURCE_OPTIONS,
                    index=(
                        SOURCE_OPTIONS.index(selected_row.get("source", SOURCE_OPTIONS[0]))
                        if selected_row.get("source") in SOURCE_OPTIONS
                        else 0
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
                height=120,
            )

            save_edit = st.form_submit_button("💾 Save Changes", use_container_width=True)

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
                    st.error(f"❌ {err}")
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
                    st.success("✅ Application updated!")
                    st.rerun()

    with delete_tab:
        st.warning(
            f"Are you sure you want to delete "
            f"**{selected_row['company']} — {selected_row['job_title']}**? "
            "This cannot be undone."
        )

        if st.button("🗑️ Yes, Delete", type="primary"):
            ok = delete_application(selected_id)

            if ok:
                st.success("Application deleted.")
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: Analytics
# ════════════════════════════════════════════════════════════════════════════════

elif page == "Analytics":
    st.title("📈 Analytics")
    st.caption("Data-driven insights into your job search. **(Data Science Feature)**")

    df = get_all_applications()

    if df.empty:
        st.info("No data to analyze yet. Add some applications or use the demo helper.")
        st.stop()

    # Smart insights
    st.subheader("💡 Smart Insights")
    insights = generate_insights(df)

    for ins in insights:
        st.markdown(
            f"""
            <div class="insight-card">
                <b>{ins['icon']} {ins['title']}</b><br>
                <span style="color:#94a3b8">{ins['body']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Charts row 1
    c1, c2 = st.columns(2)

    with c1:
        st.plotly_chart(chart_by_status(df), use_container_width=True)

    with c2:
        st.plotly_chart(chart_over_time(df), use_container_width=True)

    # Charts row 2
    c3, c4 = st.columns(2)

    with c3:
        st.plotly_chart(chart_by_job_type(df), use_container_width=True)

    with c4:
        st.plotly_chart(chart_by_source(df), use_container_width=True)

    # Charts row 3
    c5, c6 = st.columns(2)

    with c5:
        st.plotly_chart(chart_interview_rate_by_source(df), use_container_width=True)

    with c6:
        st.plotly_chart(chart_upcoming_deadlines(df, days=30), use_container_width=True)

    st.divider()

    # Raw summary table
    with st.expander("📊 View Status Summary Table"):
        summary = (
            df.groupby("status")
            .agg(
                Count=("id", "count"),
            )
            .reset_index()
        )

        st.dataframe(summary, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: AI Assistant
# ════════════════════════════════════════════════════════════════════════════════

elif page == "AI Assistant":
    st.title("🤖 AI Job Preparation Assistant")
    st.caption("Get tailored insights from your job descriptions. **(AI Bonus Feature)**")

    st.info(
        "⚠️ **Responsible AI Notice:** AI suggestions are generated automatically and may not be "
        "fully accurate. Always review and personalize them before use. They are meant to support "
        "your preparation, not replace your own judgment.",
        icon="ℹ️",
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

            with st.expander("📄 Preview Job Description"):
                st.text(
                    job_description[:1000]
                    + ("…" if len(job_description) > 1000 else "")
                )
        else:
            st.warning(
                "This application does not have a saved job description. "
                "Paste one below to analyze it."
            )

            job_description = st.text_area(
                "Job Description *",
                placeholder="Paste the job description for this application…",
                height=250,
                max_chars=4000,
            )

    else:
        company = st.text_input("Company (optional)", placeholder="e.g. Google")
        job_title = st.text_input("Job Title (optional)", placeholder="e.g. Data Analyst Intern")
        job_description = st.text_area(
            "Job Description *",
            placeholder="Paste the full job description here…",
            height=250,
            max_chars=4000,
        )

    if st.button("🚀 Analyze Job Description", type="primary", use_container_width=True):
        if not job_description or len(job_description.strip()) < 30:
            st.error("Please provide a job description with at least 30 characters.")
        else:
            with st.spinner("Analyzing… this may take a few seconds ⏳"):
                result = analyze_job_description(job_description, company, job_title)

            if result["source"] == "openai":
                st.success("✅ Analysis generated using OpenAI GPT.")
            elif result["source"] == "fallback":
                st.warning(
                    "⚠️ OpenAI API key not configured. "
                    "Showing rule-based analysis instead."
                )
            elif result["source"] == "error":
                st.error(result["content"])

            if result["source"] != "error":
                st.divider()
                st.markdown(result["content"])

                st.divider()
                st.download_button(
                    "📥 Download Analysis",
                    data=result["content"],
                    file_name=f"gradpath_analysis_{company or 'job'}.md".replace(" ", "_"),
                    mime="text/markdown",
                )


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: About
# ════════════════════════════════════════════════════════════════════════════════

elif page == "About":
    st.title("ℹ️ About GradPath AI")

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

## AI Feature: Job Preparation Assistant

The **AI Job Preparation Assistant** analyzes job descriptions and returns:

- A plain-language job summary
- Key required skills
- Resume keywords
- Interview preparation topics
- A follow-up email draft
- Practical next steps

When an OpenAI API key is configured, the app uses OpenAI's `gpt-4o-mini` model. If no API key is configured, the app uses a rule-based fallback analyzer that detects common keywords across technical, business, marketing, finance, education, healthcare, design, HR, legal, and soft-skill categories.

The fallback does not use generative AI. It exists so the app remains functional during development and demos even without API access.

---

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

---

## Responsible AI Usage

AI-generated suggestions are intended as preparation support only. They may not be fully accurate or complete. Users should review, personalize, and verify all generated content before using it in real applications or interviews.

---

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
```

---

## Tasks completed without AI assistance

- Database schema design and Supabase setup
- Form validation logic (validation.py)
- Filter and sort logic for applications (applications.py)
- Smart insight generation rules (analytics.py)
- Fallback rule-based analyzer (ai_utils.py)
- Page layout and navigation structure
- README and documentation
    """)