
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from pathlib import Path
import math


# =====================================================
# 1. DATABASE CONFIGURATION
# =====================================================

DB_NAME = Path(__file__).resolve().parent / "Timetable_Project1.db"

SESSION_TYPES = [
    "Lecture Hours",
    "Lab Hours",
    "Tutorial Hours"
]


def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =====================================================
# 2. CREATE DATABASE TABLES
# =====================================================

def create_tables():

    with connect_db() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                contact_email TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS timetable_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_id INTEGER NOT NULL,
                course_name TEXT NOT NULL,
                scheduled_date TEXT NOT NULL,
                FOREIGN KEY (department_id)
                    REFERENCES departments(department_id)
                    ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS session_allocations (
                allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER NOT NULL,
                session_type TEXT NOT NULL,
                allocated_value REAL NOT NULL
                    CHECK(allocated_value >= 0),
                FOREIGN KEY (entry_id)
                    REFERENCES timetable_entries(entry_id)
                    ON DELETE CASCADE
            )
        """)


# =====================================================
# 3. INSERT SAMPLE DATA
# =====================================================

def seed_data():

    with connect_db() as conn:

        counts = [
            conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            for table in [
                "departments",
                "timetable_entries",
                "session_allocations"
            ]
        ]

        # Seed only if all three tables are empty

        if counts == [0, 0, 0]:

            departments = [
                ("Computer Science", "cs@university.edu"),
                ("Mechanical Engineering", "mech@university.edu"),
                ("Electronics", "ece@university.edu"),
                ("Mathematics", "math@university.edu"),
                ("Data Science", "ds@university.edu")
            ]

            conn.executemany("""
                INSERT INTO departments
                (department_name, contact_email)
                VALUES (?, ?)
            """, departments)

            entries = [
                (1, "Data Structures", "2026-11-05"),
                (1, "Database Management", "2026-11-06"),
                (2, "Thermodynamics", "2026-11-07"),
                (3, "Digital Electronics", "2026-11-08"),
                (4, "Linear Algebra", "2026-11-09"),
                (5, "Statistics", "2026-11-10")
            ]

            conn.executemany("""
                INSERT INTO timetable_entries
                (department_id, course_name, scheduled_date)
                VALUES (?, ?, ?)
            """, entries)

            allocations = [
                (1, "Lecture Hours", 3),
                (1, "Lab Hours", 2),
                (2, "Lecture Hours", 3),
                (2, "Tutorial Hours", 1),
                (3, "Lecture Hours", 4),
                (3, "Lab Hours", 2),
                (4, "Lecture Hours", 3),
                (5, "Tutorial Hours", 2),
                (6, "Lecture Hours", 3),
                (6, "Lab Hours", 2)
            ]

            conn.executemany("""
                INSERT INTO session_allocations
                (entry_id, session_type, allocated_value)
                VALUES (?, ?, ?)
            """, allocations)


# =====================================================
# 4. APPLICATION WINDOW
# =====================================================

root = tk.Tk()

root.title("University Timetable Scheduling Dashboard")
root.geometry("1450x900")
root.minsize(1100, 700)

# Midnight Blue and Gold Theme

COLORS = {
    "navy": "#14213D",
    "dark_navy": "#0B162B",
    "blue": "#253B64",
    "gold": "#D4A84F",
    "gold_light": "#F4E5C1",
    "background": "#F5F2EA",
    "white": "#FFFFFF",
    "text": "#273449",
    "border": "#D8D1C3",
    "alternate": "#F1F4F8",
    "danger": "#A63D40"
}

root.configure(bg=COLORS["background"])


# =====================================================
# 5. STYLING
# =====================================================

style = ttk.Style()

try:
    style.theme_use("clam")
except tk.TclError:
    pass


style.configure(
    "TFrame",
    background=COLORS["background"]
)

style.configure(
    "TLabel",
    background=COLORS["white"],
    foreground=COLORS["text"],
    font=("Arial", 10)
)

style.configure(
    "TEntry",
    fieldbackground=COLORS["white"],
    foreground=COLORS["text"],
    padding=8
)

style.configure(
    "TCombobox",
    fieldbackground=COLORS["white"],
    background=COLORS["gold_light"],
    foreground=COLORS["text"],
    padding=8
)

style.map(
    "TCombobox",
    fieldbackground=[
        ("readonly", COLORS["white"])
    ]
)

style.configure(
    "TButton",
    background=COLORS["navy"],
    foreground=COLORS["white"],
    font=("Arial", 10, "bold"),
    padding=(13, 9),
    borderwidth=0
)

style.map(
    "TButton",
    background=[
        ("active", COLORS["blue"]),
        ("pressed", COLORS["dark_navy"])
    ],
    foreground=[
        ("active", COLORS["white"])
    ]
)

style.configure(
    "TNotebook",
    background=COLORS["background"],
    borderwidth=0
)

style.configure(
    "TNotebook.Tab",
    background=COLORS["gold_light"],
    foreground=COLORS["navy"],
    font=("Arial", 10, "bold"),
    padding=[16, 11]
)

style.map(
    "TNotebook.Tab",
    background=[
        ("selected", COLORS["navy"]),
        ("active", COLORS["gold"])
    ],
    foreground=[
        ("selected", COLORS["white"]),
        ("active", COLORS["navy"])
    ]
)

style.configure(
    "Treeview",
    background=COLORS["white"],
    fieldbackground=COLORS["white"],
    foreground=COLORS["text"],
    rowheight=32,
    font=("Arial", 10),
    borderwidth=0
)

style.configure(
    "Treeview.Heading",
    background=COLORS["navy"],
    foreground=COLORS["white"],
    font=("Arial", 10, "bold"),
    padding=10
)

style.map(
    "Treeview",
    background=[
        ("selected", COLORS["gold_light"])
    ],
    foreground=[
        ("selected", COLORS["navy"])
    ]
)

style.configure(
    "TLabelframe",
    background=COLORS["white"],
    bordercolor=COLORS["border"],
    relief="solid",
    padding=8
)

style.configure(
    "TLabelframe.Label",
    background=COLORS["background"],
    foreground=COLORS["navy"],
    font=("Arial", 11, "bold")
)


# =====================================================
# 6. HEADER
# =====================================================

header = tk.Frame(
    root,
    bg=COLORS["navy"],
    height=110
)

header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="UNIVERSITY TIMETABLE MANAGEMENT SYSTEM",
    bg=COLORS["navy"],
    fg=COLORS["white"],
    font=("Arial", 24, "bold")
).pack(pady=(19, 5))

tk.Label(
    header,
    text="RELATIONAL DATABASE  |  SESSION ALLOCATION DASHBOARD",
    bg=COLORS["navy"],
    fg=COLORS["gold"],
    font=("Arial", 10, "bold")
).pack()


# =====================================================
# 7. INPUT VARIABLES
# =====================================================

dept_var = tk.StringVar()
email_var = tk.StringVar()
course_var = tk.StringVar()
date_var = tk.StringVar(value=date.today().isoformat())
session_var = tk.StringVar(value=SESSION_TYPES[0])
value_var = tk.StringVar()


# =====================================================
# 8. INSERT PANEL
# =====================================================

insert_frame = ttk.LabelFrame(
    root,
    text="  ADD NEW TIMETABLE RECORD  ",
    padding=15
)

insert_frame.pack(
    fill="x",
    padx=18,
    pady=12
)

fields = [
    ("Department Name", dept_var, 0, 0),
    ("Contact Email (for new departments)", email_var, 0, 2),
    ("Course Name", course_var, 0, 4),
    ("Scheduled Date (YYYY-MM-DD)", date_var, 2, 0),
    ("Allocated Value", value_var, 2, 4)
]

for label, variable, row, col in fields:

    ttk.Label(
        insert_frame,
        text=label
    ).grid(
        row=row,
        column=col,
        sticky="w",
        padx=8,
        pady=5
    )

    ttk.Entry(
        insert_frame,
        textvariable=variable,
        width=30
    ).grid(
        row=row + 1,
        column=col,
        padx=8,
        pady=5,
        sticky="ew"
    )


ttk.Label(
    insert_frame,
    text="Session Type"
).grid(
    row=2,
    column=2,
    sticky="w",
    padx=8,
    pady=5
)

session_dropdown = ttk.Combobox(
    insert_frame,
    textvariable=session_var,
    values=SESSION_TYPES,
    state="readonly",
    width=27
)

session_dropdown.grid(
    row=3,
    column=2,
    padx=8,
    pady=5,
    sticky="ew"
)

for col in [0, 2, 4]:
    insert_frame.grid_columnconfigure(col, weight=1)


# =====================================================
# 9. INSERT RECORD FUNCTION
# =====================================================

def add_record():

    department = dept_var.get().strip()
    email = email_var.get().strip()
    course = course_var.get().strip()
    scheduled = date_var.get().strip()
    session = session_var.get().strip()
    value_text = value_var.get().strip()

    if not all([
        department,
        course,
        scheduled,
        session,
        value_text
    ]):

        messagebox.showwarning(
            "Validation",
            "Please fill all required fields."
        )
        return

    if session not in SESSION_TYPES:

        messagebox.showwarning(
            "Invalid Session",
            "Please select a valid session type."
        )
        return

    try:

        datetime.strptime(scheduled, "%Y-%m-%d")

    except ValueError:

        messagebox.showerror(
            "Invalid Date",
            "Enter date in YYYY-MM-DD format."
        )
        return

    try:

        allocated = float(value_text)

        if not math.isfinite(allocated) or allocated < 0:
            raise ValueError

    except ValueError:

        messagebox.showerror(
            "Invalid Value",
            "Allocated value must be a non-negative number."
        )
        return

    try:

        with connect_db() as conn:

            result = conn.execute("""
                SELECT department_id
                FROM departments
                WHERE department_name = ?
            """, (department,)).fetchone()

            if result:

                dept_id = result[0]

            else:

                if not email:

                    messagebox.showwarning(
                        "Email Required",
                        "Enter contact email for a new department."
                    )
                    return

                if "@" not in email or "." not in email.split("@")[-1]:

                    messagebox.showwarning(
                        "Invalid Email",
                        "Please enter a valid contact email."
                    )
                    return

                cursor = conn.execute("""
                    INSERT INTO departments
                    (department_name, contact_email)
                    VALUES (?, ?)
                """, (department, email))

                dept_id = cursor.lastrowid

            cursor = conn.execute("""
                INSERT INTO timetable_entries
                (department_id, course_name, scheduled_date)
                VALUES (?, ?, ?)
            """, (dept_id, course, scheduled))

            entry_id = cursor.lastrowid

            conn.execute("""
                INSERT INTO session_allocations
                (entry_id, session_type, allocated_value)
                VALUES (?, ?, ?)
            """, (entry_id, session, allocated))

        # Clear fields after successful insertion

        dept_var.set("")
        email_var.set("")
        course_var.set("")
        date_var.set(date.today().isoformat())
        session_var.set(SESSION_TYPES[0])
        value_var.set("")

        refresh_all()

        messagebox.showinfo(
            "Success",
            f"Record added successfully!\n\n"
            f"Department ID: {dept_id}\n"
            f"Timetable Entry ID: {entry_id}"
        )

    except sqlite3.Error as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )


ttk.Button(
    insert_frame,
    text="ADD TIMETABLE RECORD",
    command=add_record
).grid(
    row=4,
    column=0,
    columnspan=6,
    pady=13
)


# =====================================================
# 10. DELETE PANEL
# =====================================================

delete_type_var = tk.StringVar(value="Department")
delete_var = tk.StringVar()

delete_map = {}

delete_frame = ttk.LabelFrame(
    root,
    text="  DELETE DATABASE RECORD  ",
    padding=15
)

delete_frame.pack(
    fill="x",
    padx=18,
    pady=8
)

ttk.Label(
    delete_frame,
    text="Select Record Type:"
).grid(
    row=0,
    column=0,
    padx=8,
    pady=8
)

delete_type_dropdown = ttk.Combobox(
    delete_frame,
    textvariable=delete_type_var,
    values=[
        "Department",
        "Timetable Entry",
        "Session Allocation"
    ],
    state="readonly",
    width=23
)

delete_type_dropdown.grid(
    row=0,
    column=1,
    padx=8,
    pady=8
)

ttk.Label(
    delete_frame,
    text="Select Record:"
).grid(
    row=0,
    column=2,
    padx=8,
    pady=8
)

delete_dropdown = ttk.Combobox(
    delete_frame,
    textvariable=delete_var,
    state="readonly",
    width=48
)

delete_dropdown.grid(
    row=0,
    column=3,
    padx=8,
    pady=8
)


# =====================================================
# 11. UPDATE DELETE OPTIONS
# =====================================================

def update_delete_options(event=None):

    global delete_map

    record_type = delete_type_var.get()

    with connect_db() as conn:

        if record_type == "Department":

            rows = conn.execute("""
                SELECT department_id, department_name
                FROM departments
                ORDER BY department_id
            """).fetchall()

            options = [
                (i, f"Department ID {i} - {name}")
                for i, name in rows
            ]

        elif record_type == "Timetable Entry":

            rows = conn.execute("""
                SELECT entry_id, course_name, scheduled_date
                FROM timetable_entries
                ORDER BY entry_id
            """).fetchall()

            options = [
                (
                    i,
                    f"Entry ID {i} - {name} ({scheduled})"
                )
                for i, name, scheduled in rows
            ]

        else:

            rows = conn.execute("""
                SELECT
                    allocation_id,
                    entry_id,
                    session_type,
                    allocated_value
                FROM session_allocations
                ORDER BY allocation_id
            """).fetchall()

            options = [
                (
                    i,
                    f"Allocation ID {i} - Entry {entry} - "
                    f"{session} ({value:g})"
                )
                for i, entry, session, value in rows
            ]

    delete_map = {
        label: record_id
        for record_id, label in options
    }

    delete_dropdown["values"] = list(delete_map.keys())
    delete_var.set("")


delete_type_dropdown.bind(
    "<<ComboboxSelected>>",
    update_delete_options
)


# =====================================================
# 12. DELETE RECORD FUNCTION
# =====================================================

def delete_record():

    selected = delete_var.get()
    record_type = delete_type_var.get()

    if not selected or selected not in delete_map:

        messagebox.showwarning(
            "Warning",
            "Please select a record."
        )
        return

    record_id = delete_map[selected]

    if not messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete:\n\n{selected}?"
    ):
        return

    tables = {
        "Department": ("departments", "department_id"),
        "Timetable Entry": ("timetable_entries", "entry_id"),
        "Session Allocation": (
            "session_allocations",
            "allocation_id"
        )
    }

    table, column = tables[record_type]

    try:

        with connect_db() as conn:

            cursor = conn.execute(
                f"DELETE FROM {table} WHERE {column} = ?",
                (record_id,)
            )

            deleted = cursor.rowcount

        refresh_all()

        if deleted:

            messagebox.showinfo(
                "Success",
                "Record deleted successfully!"
            )

        else:

            messagebox.showwarning(
                "Not Found",
                "The selected record no longer exists."
            )

    except sqlite3.Error as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )


ttk.Button(
    delete_frame,
    text="DELETE SELECTED",
    command=delete_record
).grid(
    row=0,
    column=4,
    padx=12
)


# =====================================================
# 13. DATABASE DISPLAY PANEL
# =====================================================

records_frame = ttk.LabelFrame(
    root,
    text="  DATABASE RECORDS  ",
    padding=10
)

records_frame.pack(
    fill="both",
    expand=True,
    padx=18,
    pady=10
)

notebook = ttk.Notebook(records_frame)

notebook.pack(
    fill="both",
    expand=True
)


# =====================================================
# 14. CREATE TABLE TABS
# =====================================================

def create_table_tab(title):

    tab = ttk.Frame(notebook)

    notebook.add(
        tab,
        text=title
    )

    frame = ttk.Frame(tab)

    frame.pack(
        fill="both",
        expand=True
    )

    scroll_y = ttk.Scrollbar(
        frame,
        orient="vertical"
    )

    scroll_x = ttk.Scrollbar(
        frame,
        orient="horizontal"
    )

    tree = ttk.Treeview(
        frame,
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set,
        show="headings"
    )

    scroll_y.config(
        command=tree.yview
    )

    scroll_x.config(
        command=tree.xview
    )

    scroll_y.pack(
        side="right",
        fill="y"
    )

    scroll_x.pack(
        side="bottom",
        fill="x"
    )

    tree.pack(
        fill="both",
        expand=True
    )

    tree.tag_configure(
        "even",
        background=COLORS["white"]
    )

    tree.tag_configure(
        "odd",
        background=COLORS["alternate"]
    )

    return tree


join_tree = create_table_tab("Combined JOIN View")
dept_tree = create_table_tab("Departments")
entry_tree = create_table_tab("Timetable Entries")
allocation_tree = create_table_tab("Session Allocations")


# =====================================================
# 15. DISPLAY TABLE DATA
# =====================================================

def display_data(tree, columns, rows):

    tree.delete(*tree.get_children())

    tree["columns"] = columns
    tree["show"] = "headings"

    for col in columns:

        tree.heading(
            col,
            text=col.replace("_", " ").title()
        )

        tree.column(
            col,
            width=165,
            minwidth=100,
            anchor="center"
        )

    for index, row in enumerate(rows):

        tag = "even" if index % 2 == 0 else "odd"

        tree.insert(
            "",
            "end",
            values=row,
            tags=(tag,)
        )


# =====================================================
# 16. REFRESH ALL FOUR TABLES
# =====================================================

def refresh_all():

    with connect_db() as conn:

        # Combined JOIN View

        rows = conn.execute("""
            SELECT
                te.entry_id,
                d.department_name,
                te.course_name,
                te.scheduled_date,
                sa.session_type,
                sa.allocated_value
            FROM departments d
            JOIN timetable_entries te
                ON d.department_id = te.department_id
            JOIN session_allocations sa
                ON te.entry_id = sa.entry_id
            ORDER BY te.entry_id, sa.allocation_id
        """).fetchall()

        display_data(
            join_tree,
            [
                "Entry ID",
                "Department Name",
                "Course Name",
                "Scheduled Date",
                "Session Type",
                "Allocated Value"
            ],
            rows
        )

        # Departments

        rows = conn.execute("""
            SELECT *
            FROM departments
            ORDER BY department_id
        """).fetchall()

        display_data(
            dept_tree,
            [
                "Department ID",
                "Department Name",
                "Contact Email"
            ],
            rows
        )

        # Timetable Entries

        rows = conn.execute("""
            SELECT *
            FROM timetable_entries
            ORDER BY entry_id
        """).fetchall()

        display_data(
            entry_tree,
            [
                "Entry ID",
                "Department ID",
                "Course Name",
                "Scheduled Date"
            ],
            rows
        )

        # Session Allocations

        rows = conn.execute("""
            SELECT *
            FROM session_allocations
            ORDER BY allocation_id
        """).fetchall()

        display_data(
            allocation_tree,
            [
                "Allocation ID",
                "Entry ID",
                "Session Type",
                "Allocated Value"
            ],
            rows
        )

    # Refresh delete dropdown after every operation

    update_delete_options()


# =====================================================
# 17. START APPLICATION
# =====================================================

def main():

    try:

        create_tables()
        seed_data()
        refresh_all()

        root.mainloop()

    except sqlite3.Error as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )

    except Exception as error:

        messagebox.showerror(
            "Application Error",
            str(error)
        )


if __name__ == "__main__":
    main()
