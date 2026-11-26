import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# Website settings
st.set_page_config(
    page_title="TaskFlow",
    page_icon="✅",
    layout="wide"
)

# Create database
conn = sqlite3.connect("tasks.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT,
    deadline TEXT,
    status TEXT
)
""")

conn.commit()

# Sidebar
st.sidebar.title("✅ TaskFlow")
st.sidebar.write("Your personal task manager")
st.sidebar.divider()
st.sidebar.info("Built with Python, Streamlit and SQLite")

# Main page
st.title("✅ TaskFlow")
st.caption("Organise your tasks and track your progress.")

# Add tasks
st.subheader("➕ Create Task")

with st.form("add_task", clear_on_submit=True):

    title = st.text_input("Task Title")
    description = st.text_area("Description")

    priority = st.selectbox(
        "Priority",
        ["Low", "Medium", "High"]
    )

    deadline = st.date_input("Deadline", date.today())

    submitted = st.form_submit_button(
        "Add Task",
        type="primary"
    )

    if submitted:
        if title.strip():
            conn.execute(
                """INSERT INTO tasks
                (title, description, priority, deadline, status)
                VALUES (?, ?, ?, ?, ?)""",
                (
                    title.strip(),
                    description,
                    priority,
                    str(deadline),
                    "Pending"
                )
            )

            conn.commit()
            st.success("Task added successfully!")
            st.rerun()

        else:
            st.error("Please enter a task title.")

# Load tasks
df = pd.read_sql_query(
    "SELECT * FROM tasks ORDER BY deadline ASC",
    conn
)

# Dashboard
st.divider()
st.subheader("📊 Task Overview")

total = len(df)
completed = len(df[df["status"] == "Completed"])
pending = len(df[df["status"] == "Pending"])

col1, col2, col3 = st.columns(3)

col1.metric("Total Tasks", total)
col2.metric("Completed", completed)
col3.metric("Pending", pending)

st.divider()

# Task list
st.subheader("📋 Your Tasks")

if df.empty:
    st.info("No tasks yet. Create your first task above.")

else:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Pending", "Completed"]
    )

    if status_filter != "All":
        filtered = df[df["status"] == status_filter]
    else:
        filtered = df

    st.dataframe(
        filtered[
            ["title", "description", "priority", "deadline", "status"]
        ],
        hide_index=True,
        use_container_width=True
    )

    # Update task status
    st.subheader("✔️ Update Task Status")

    task_id = st.selectbox(
        "Select Task",
        df["id"].tolist(),
        format_func=lambda x: (
            df.loc[df["id"] == x, "title"].iloc[0]
        )
    )

    new_status = st.selectbox(
        "New Status",
        ["Pending", "Completed"]
    )

    if st.button("Update Status"):
        conn.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (new_status, task_id)
        )

        conn.commit()
        st.rerun()

        # Edit task
    st.subheader("✏️ Edit Task")

    edit_id = st.selectbox(
        "Select Task to Edit",
        df["id"].tolist(),
        format_func=lambda x: df.loc[
            df["id"] == x, "title"
        ].iloc[0]
    )

    selected_task = df[df["id"] == edit_id].iloc[0]

    with st.form("edit_task"):
        edited_title = st.text_input(
            "Edit Title",
            value=selected_task["title"]
        )

        edited_description = st.text_area(
            "Edit Description",
            value=selected_task["description"] or ""
        )

        edited_priority = st.selectbox(
            "Edit Priority",
            ["Low", "Medium", "High"],
            index=["Low", "Medium", "High"].index(
                selected_task["priority"]
            )
        )

        edited_deadline = st.date_input(
            "Edit Deadline",
            value=date.fromisoformat(selected_task["deadline"])
        )

        save_changes = st.form_submit_button("Save Changes")

        if save_changes:
            if not edited_title.strip():
                st.error("Task title cannot be empty.")
            else:
                conn.execute(
                    """UPDATE tasks
                    SET title = ?, description = ?,
                        priority = ?, deadline = ?
                    WHERE id = ?""",
                    (
                        edited_title.strip(),
                        edited_description,
                        edited_priority,
                        str(edited_deadline),
                        edit_id
                    )
                )
                conn.commit()
                st.rerun()
    
    # Delete task
    st.subheader("🗑️ Delete Task")

    delete_id = st.selectbox(
        "Select Task to Delete",
        df["id"].tolist(),
        format_func=lambda x: (
            df.loc[df["id"] == x, "title"].iloc[0]
        )
    )

    if st.button("Delete Task"):
        conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (delete_id,)
        )

        conn.commit()
        st.rerun()

conn.close()