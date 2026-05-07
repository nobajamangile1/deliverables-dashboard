import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
import os

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NJ Deliverables Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:        #0c0c0f;
    --surface:   #131318;
    --surface2:  #1a1a23;
    --border:    #2a2a38;
    --accent:    #c8f135;
    --accent2:   #7c6af7;
    --danger:    #f15b5b;
    --text:      #e8e8f0;
    --muted:     #6b6b88;
    --high:      #f15b5b;
    --med:       #f5a623;
    --low:       #5bcef1;
}

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background: var(--bg);
    color: var(--text);
}

/* Header */
.dash-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 28px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
}
.dash-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    color: var(--accent);
    letter-spacing: -0.03em;
    margin: 0;
}
.dash-subtitle {
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

/* KPI cards */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent);
}
.kpi-label {
    font-size: 0.65rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.18em;
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 2.2rem;
    color: var(--text);
    line-height: 1;
}
.kpi-value.accent { color: var(--accent); }
.kpi-value.purple { color: var(--accent2); }

/* Section headers */
.section-head {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 28px 0 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-head::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* Priority badges */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.badge-high   { background: rgba(241,91,91,0.15);  color: var(--high); border: 1px solid rgba(241,91,91,0.3); }
.badge-medium { background: rgba(245,166,35,0.15); color: var(--med);  border: 1px solid rgba(245,166,35,0.3); }
.badge-low    { background: rgba(91,206,241,0.15); color: var(--low);  border: 1px solid rgba(91,206,241,0.3); }

/* Task expander rows */
.task-row {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 8px;
    transition: border-color 0.2s;
}
.task-row:hover { border-color: var(--accent2); }
.task-name-lbl { font-weight: 500; font-size: 0.9rem; color: var(--text); }
.task-meta     { font-size: 0.72rem; color: var(--muted); margin-top: 4px; }

/* Buttons */
.stButton > button {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--surface2);
    color: var(--text);
    transition: all 0.18s;
}
.stButton > button:hover {
    border-color: var(--accent);
    color: var(--accent);
    background: rgba(200,241,53,0.06);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stSelectbox div,
section[data-testid="stSidebar"] .stDateInput input {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace;
}

/* DataFrames */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Metrics override */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.7rem; letter-spacing: 0.15em; }
[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif; color: var(--accent); }

/* Divider */
hr { border-color: var(--border); }

/* Archive notice */
.archive-note {
    background: rgba(124,106,247,0.08);
    border: 1px solid rgba(124,106,247,0.25);
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.78rem;
    color: var(--accent2);
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Database helpers ────────────────────────────────────────────────────────────
DB_PATH = "/tmp/deliverables.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        with get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deliverables (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name        TEXT NOT NULL,
                    category         TEXT,
                    priority         TEXT,
                    status           TEXT DEFAULT 'Pending',
                    due_date         DATE,
                    efficiency_score INTEGER,
                    archived         INTEGER DEFAULT 0,
                    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS archive_log (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    task_count  INTEGER
                )
            """)
            conn.commit()
    except Exception as e:
        st.error(f"DB init error: {e}")

def fetch_active():
    try:
        with get_conn() as conn:
            return pd.read_sql_query(
                "SELECT * FROM deliverables WHERE archived=0 ORDER BY due_date ASC, priority DESC",
                conn
            )
    except Exception as e:
        st.error(f"Fetch error: {e}")
        return pd.DataFrame()

def fetch_completed_archived():
    try:
        with get_conn() as conn:
            return pd.read_sql_query(
                "SELECT * FROM deliverables WHERE archived=1 ORDER BY created_at DESC LIMIT 50",
                conn
            )
    except Exception as e:
        return pd.DataFrame()

def add_task(task_name, category, priority, due_date):
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO deliverables (task_name, category, priority, due_date, status) VALUES (?,?,?,?,?)",
                (task_name, category, priority, str(due_date), "Pending")
            )
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Insert error: {e}")
        return False

def mark_complete(task_id, score):
    try:
        with get_conn() as conn:
            conn.execute(
                "UPDATE deliverables SET status=?, efficiency_score=? WHERE id=?",
                ("Completed", score, task_id)
            )
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Update error: {e}")
        return False

def mark_in_progress(task_id):
    try:
        with get_conn() as conn:
            conn.execute("UPDATE deliverables SET status='In Progress' WHERE id=?", (task_id,))
            conn.commit()
    except Exception as e:
        st.error(f"Update error: {e}")

def delete_task(task_id):
    try:
        with get_conn() as conn:
            conn.execute("DELETE FROM deliverables WHERE id=?", (task_id,))
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Delete error: {e}")
        return False

def daily_reset():
    try:
        with get_conn() as conn:
            cur = conn.execute(
                "SELECT COUNT(*) FROM deliverables WHERE status='Completed' AND archived=0"
            )
            count = cur.fetchone()[0]
            if count > 0:
                conn.execute(
                    "UPDATE deliverables SET archived=1 WHERE status='Completed' AND archived=0"
                )
                conn.execute("INSERT INTO archive_log (task_count) VALUES (?)", (count,))
                conn.commit()
            return count
    except Exception as e:
        st.error(f"Reset error: {e}")
        return 0

# ── KPI computations ────────────────────────────────────────────────────────────
def compute_kpis(df):
    total = len(df)
    completed = len(df[df["status"] == "Completed"])
    rate = round((completed / total * 100) if total > 0 else 0, 1)
    scores = df[df["efficiency_score"].notna()]["efficiency_score"]
    avg_eff = round(scores.mean(), 1) if len(scores) > 0 else 0.0
    return total, rate, avg_eff

# ── Init ────────────────────────────────────────────────────────────────────────
init_db()

if "refresh" not in st.session_state:
    st.session_state.refresh = 0
if "complete_target" not in st.session_state:
    st.session_state.complete_target = None

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
    <span class="dash-title">⚡ DELIVERABLES</span>
    <span class="dash-subtitle">Accountability Dashboard</span>
</div>
""", unsafe_allow_html=True)

# ── Sidebar — Add Task ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="dash-title" style="font-size:1.1rem;">＋ New Task</p>', unsafe_allow_html=True)
    with st.form("add_form", clear_on_submit=True):
        task_name = st.text_input("Task Name *", placeholder="e.g. Draft Q2 risk report")
        category  = st.selectbox("Category", ["Deep Work", "Admin", "Health", "Personal", "Strategic"])
        priority  = st.selectbox("Priority", ["High", "Medium", "Low"])
        due_date  = st.date_input("Due Date", value=date.today())
        submitted = st.form_submit_button("⚡ Add Deliverable", use_container_width=True)

        if submitted:
            if not task_name.strip():
                st.error("Task name cannot be empty.")
            else:
                if add_task(task_name.strip(), category, priority, due_date):
                    st.success("Task added.")
                    st.session_state.refresh += 1

    st.divider()
    st.markdown('<p style="font-size:0.7rem;color:#6b6b88;text-transform:uppercase;letter-spacing:0.15em;">Daily Operations</p>', unsafe_allow_html=True)
    if st.button("🗂️ Daily Reset — Archive Completed", use_container_width=True):
        n = daily_reset()
        if n > 0:
            st.success(f"Archived {n} completed task(s).")
            st.session_state.refresh += 1
        else:
            st.info("No completed tasks to archive.")

    st.divider()
    st.markdown(f'<p style="font-size:0.65rem;color:#6b6b88;">Last refresh: {datetime.now().strftime("%H:%M:%S")}</p>', unsafe_allow_html=True)

# ── Load data ───────────────────────────────────────────────────────────────────
df = fetch_active()

# ── KPI row ─────────────────────────────────────────────────────────────────────
total, rate, avg_eff = compute_kpis(df) if not df.empty else (0, 0.0, 0.0)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("📋 Total Tasks", total)
with c2:
    st.metric("✅ Completion Rate", f"{rate}%")
with c3:
    st.metric("⚡ Avg Efficiency", f"{avg_eff}/10")
with c4:
    pending = len(df[df["status"] == "Pending"]) if not df.empty else 0
    st.metric("🔴 Pending", pending)

st.divider()

# ── Filters + Active tracker ────────────────────────────────────────────────────
st.markdown('<div class="section-head">Active Tracker</div>', unsafe_allow_html=True)

if df.empty:
    st.info("No active tasks. Add one from the sidebar.")
else:
    f1, f2, f3 = st.columns([2, 2, 3])
    with f1:
        cats = st.multiselect("Category", options=sorted(df["category"].dropna().unique()), default=[])
    with f2:
        pris = st.multiselect("Priority", options=["High", "Medium", "Low"], default=[])
    with f3:
        search = st.text_input("🔍 Search tasks", placeholder="keyword…")

    filtered = df.copy()
    if cats:
        filtered = filtered[filtered["category"].isin(cats)]
    if pris:
        filtered = filtered[filtered["priority"].isin(pris)]
    if search:
        filtered = filtered[filtered["task_name"].str.contains(search, case=False, na=False)]

    # Dataframe view
    display_cols = ["id", "task_name", "category", "priority", "status", "due_date", "efficiency_score"]
    existing_cols = [c for c in display_cols if c in filtered.columns]
    st.dataframe(
        filtered[existing_cols].rename(columns={
            "id": "ID", "task_name": "Task", "category": "Category",
            "priority": "Priority", "status": "Status",
            "due_date": "Due", "efficiency_score": "Score"
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown('<div class="section-head">Task Actions</div>', unsafe_allow_html=True)

    for _, row in filtered.iterrows():
        pri_color = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}.get(row["priority"], "badge-low")
        status_icon = {"Pending": "⏳", "In Progress": "🔄", "Completed": "✅"}.get(row["status"], "")

        with st.expander(f"{status_icon} {row['task_name']}  ·  {row['category']}  ·  Due: {row['due_date']}"):
            col_a, col_b, col_c = st.columns([3, 2, 1])
            with col_a:
                st.markdown(f"**Priority:** `{row['priority']}`  |  **Status:** `{row['status']}`")
                if row["efficiency_score"]:
                    st.markdown(f"**Efficiency Score:** `{row['efficiency_score']}/10`")

            with col_b:
                if row["status"] == "Pending":
                    if st.button("▶ Mark In Progress", key=f"prog_{row['id']}"):
                        mark_in_progress(row["id"])
                        st.session_state.refresh += 1
                        st.rerun()

                if row["status"] in ("Pending", "In Progress"):
                    st.markdown("**Complete this task:**")
                    score = st.slider("Efficiency score (1–10)", 1, 10, 7, key=f"score_{row['id']}")
                    if st.button("✅ Mark as Complete", key=f"done_{row['id']}"):
                        if mark_complete(row["id"], score):
                            st.success("Marked complete!")
                            st.session_state.refresh += 1
                            st.rerun()

            with col_c:
                if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                    if delete_task(row["id"]):
                        st.warning("Deleted.")
                        st.session_state.refresh += 1
                        st.rerun()

# ── Archive log ─────────────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">Completed Archive</div>', unsafe_allow_html=True)
arch = fetch_completed_archived()
if arch.empty:
    st.markdown('<p style="color:#6b6b88;font-size:0.8rem;">No archived tasks yet. Run Daily Reset to archive completed tasks.</p>', unsafe_allow_html=True)
else:
    arch_cols = [c for c in ["id","task_name","category","priority","due_date","efficiency_score"] if c in arch.columns]
    st.dataframe(
        arch[arch_cols].rename(columns={
            "id": "ID", "task_name": "Task", "category": "Category",
            "priority": "Priority", "due_date": "Due", "efficiency_score": "Score"
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(f'<div class="archive-note">📦 {len(arch)} archived task(s) shown.</div>', unsafe_allow_html=True)
