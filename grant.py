import matplotlib.pyplot as plt
import pandas as pd

tasks = [
    ("Project Setup & Environment Configuration", "2025-12-20", "2025-12-26"),
    ("Requirement Analysis & Planning", "2025-12-27", "2025-12-31"),
    ("UI Design (HTML, CSS, Bootstrap)", "2026-01-01", "2026-01-06"),
    ("Frontend Development", "2026-01-07", "2026-01-12"),
    ("Backend Development (Flask)", "2026-01-13", "2026-01-20"),
    ("Database Handling & Data Processing", "2026-01-21", "2026-01-25"),
    ("Demand Analysis Module", "2026-01-26", "2026-01-30"),
    ("Dynamic Pricing Algorithm Development", "2026-01-31", "2026-02-06"),
    ("Price Prediction Implementation", "2026-02-07", "2026-02-12"),
    ("Data Visualization (Graphs & Charts)", "2026-02-13", "2026-02-18"),
    ("Revenue & Profit Calculation", "2026-02-19", "2026-02-23"),
    ("Strategy Recommendation System", "2026-02-24", "2026-02-28"),
    ("Integration & Testing", "2026-03-01", "2026-03-06"),
    ("Final Deployment & Documentation", "2026-03-07", "2026-03-12"),
]

df = pd.DataFrame(tasks, columns=["Task", "Start", "End"])
df["Start"] = pd.to_datetime(df["Start"])
df["End"] = pd.to_datetime(df["End"])
df["Duration"] = (df["End"] - df["Start"]).dt.days

plt.style.use('ggplot')

fig, ax = plt.subplots(figsize=(16, 8))  # BIGGER SIZE

for i, task in enumerate(df.itertuples()):
    ax.barh(task.Task, task.Duration, left=task.Start, color="#5A8DEE")

    # ✅ ADD TEXT INSIDE BAR (like EduCheck)
    ax.text(task.Start, i, task.Task, va='center', ha='left', fontsize=8)

ax.set_title("Dynamic Pricing System Gantt Chart (Dec 2025 - Mar 2026)", fontsize=16)
ax.set_xlabel("Timeline")
ax.set_ylabel("Tasks")

ax.grid(True, linestyle='--', alpha=0.5)
ax.invert_yaxis()

plt.xticks(rotation=45)

# ✅ VERY IMPORTANT → FIX LEFT SPACE
plt.subplots_adjust(left=0.35)

plt.tight_layout()

plt.savefig("perfect_gantt.png", dpi=300)
plt.show()