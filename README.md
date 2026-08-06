# Module 1 Assignment Project – Singapore Jobs Analytics

# Group-self discussion #
1)	Cleaning of data.
-	Removing empty rows
-	Deleted two columns (‘occupationId’, ‘status_id’)
-	Removing duplicates - What criteria do you consider duplicate?
o	Check if all values except for job ID is identical. 
o	Let me know if you disocover something else. 
-	Removing anomalous data (unreasonable values for salary, min years of experience = 80)

2)	Problem Statement (important)
-	Analyze overall trends in different sectors?
-	Benchmark salary?

3)	Graphs/Tables to plot
-	TBA, adjust according to use case (with inputs from all of us.)

--- 

Design a simple data product (dashboard or web app) using a real-world CSV of Singapore job postings (~1M+ rows). Your goal is to solve a clear business problem for a specific user group using insights from the data.

> **This looks big. It isn't** — it's every small skill from Module 1, chained together: loading data, cleaning it, exploring it, and showing what you found. Follow the milestones below and you'll be fine.

## Data dictionary

| Column | Type | Notes |
| :---- | :---- | :---- |
| `categories` | str (JSON array) | e.g. `[{"id":21,"category":"Information Technology"}]` — a job can belong to **multiple** categories. You will need to parse this. |
| `employmentTypes` | str | Permanent, Full Time, Contract, Part Time, Temporary, Internship/Attachment, Freelance, Flexi-work. |
| `metadata_expiryDate` | date | When the posting expires. |
| `metadata_isPostedOnBehalf` | bool | True if a recruiter posted on behalf of the hiring company. |
| `metadata_jobPostId` | str | Unique ID, e.g. `MCF-2023-0252866`. |
| `metadata_newPostingDate` | date | Date of the most recent re-post. |
| `metadata_originalPostingDate` | date | Date the job was first posted. |
| `metadata_repostCount` | int | How many times the same job has been re-posted. A signal of hard-to-fill roles. |
| `metadata_totalNumberJobApplication` | int | Number of applications received. |
| `metadata_totalNumberOfView` | int | Number of times the post was viewed. |
| `minimumYearsExperience` | int | Years of experience required. |
| `numberOfVacancies` | int | Open headcount. |
| `positionLevels` | str | Fresh/entry, Junior Executive, Executive, Senior Executive, Professional, Manager, Middle Management, Senior Management, Non-executive. |
| `postedCompany_name` | str | The poster (often a recruitment agency, **not** the hiring employer). |
| `salary_minimum` / `salary_maximum` | int | Salary band. |
| `salary_type` | str | Almost all `Monthly`. |
| `status_jobStatus` | str | Open, Closed, Re-open. |
| `title` | str | Free-text job title. |
| `average_salary` | float | Pre-computed mean of min/max. |

---


---

## 🚀 Getting Started (do this first)

**Step 0 — Load a sample, not the whole file.** The full file has ~1M rows; taste a spoonful before cooking the whole pot. Build everything on the fast subset, and scale up once it works:

```python
import pandas as pd
df = pd.read_csv('sg_jobs.csv', nrows=50000)   # first 50,000 rows only
```

**Then take your first three EDA steps** (adjust column names to what's actually in the file):

```python
df.shape                    # 1. How big is your sample? (rows, columns)
df.info()                   # 2. What columns do you have, and what types are they?
df['salary'].describe()     # 3. Pick one numeric column — what's typical, what's extreme?
```

That's it — you've started. Everything else in this brief builds on these first looks.

**Where to get the dataset:** [Dataset link — provided by your instructor]

---

## 🗓️ Suggested Milestones

A gentle ramp so you're never cramming at the end:

| Week | You should have... |
|------|--------------------|
| **Week 1** | Business case chosen + data loaded (sample first!) + first EDA done |
| **Week 2** | Cleaning + feature engineering + your key charts drafted |
| **Week 3** | Dashboard assembled + story polished + presentation rehearsed |

---

## 1. Business Case (2–3 bullets)

Briefly describe:

- Business scenario (e.g. talent acquisition, policy analyst, career coach).
- **Objective**: What decision/problem are you helping to address?
- Target users and value: How will this dashboard/app help them?

> Example: “Help a talent acquisition team identify which roles and skills are most in demand so they can prioritise hiring and sourcing.”

---

## 2. Data Handling & Process (5–8 bullets)

Summarise your end-to-end process:

- Tools used (e.g. Python + Pandas / DuckDB / SQL).
- How you loaded the CSV (~1M+ rows).
- Key cleaning steps (missing values, standardising categories, parsing dates, handling salary formats).
- Important feature engineering (e.g. seniority, salary bands, demand metrics, skill tags).
- EDA highlights: key patterns or anomalies you discovered that shaped your dashboard design.

You do not need to show all code, but the logic and key decisions should be clear.

---

## 3. Dashboard / App (6–10 bullets)

Describe and demonstrate your solution:

- Type of solution: dashboard (e.g. Streamlit, Power BI, Tableau) or simple web app.
- Main views:
  - Overview metrics (e.g. total postings, top roles/industries, salary ranges).
  - Drill-down view (by role, industry, location, skills, etc.).
  - Time trend view (e.g. postings over time, salary trends).
- Interactivity: filters, sorting, drill-downs, tooltips where relevant.
- Design choices: layout, chart types, colour scheme, readability.
- How each view directly supports your business objective and target users.

Include 2–4 key screenshots in your written submission (or show live in the presentation).

---

## 4. Presentation (10 mins per team)

Suggested flow:

1. **Business case & objective** (2–3 mins)  
   - Scenario, users, objective, success criteria.
2. **Process & data handling** (3–4 mins)  
   - How you cleaned, transformed, and explored the data.
3. **Dashboard / app walkthrough** (3–4 mins)  
   - Main views, interactions, and how they answer the business question.
4. **Challenges & learnings** (1–2 mins)  
   - Technical/analytical challenges, what you learned, and possible next steps.

---

## 5. Deliverables

- Brief written report (Markdown/PDF) following Sections 1–4 above.
- Working dashboard / app (deployed link or clear run instructions).
- Code repo with:
  - Data handling notebook(s) / scripts,
  - Dashboard/app code,
  - README with setup steps.

Focus on a **coherent story** from business question → data process → dashboard → insights, rather than advanced techniques.

---

## 📊 How You'll Be Assessed

| Criterion | Weight | What excellent looks like |
|-----------|--------|---------------------------|
| Business case clarity | 20% | A specific user, a specific decision, and a clear reason your dashboard helps them make it. |
| Data handling & cleaning | 25% | Cleaning choices are explained and justified — we can see *why* you handled missing values or salary formats the way you did. |
| Dashboard functionality | 25% | Views load, filters work, and each element answers part of the business question. |
| Insight & story | 20% | Findings are framed as answers ("Roles X and Y are surging in the East"), not just charts. |
| Presentation | 10% | Clear, within time, everyone contributes, and the demo lands. |

**To pass:** a working dashboard with at least one overview view and one drill-down, tied to a stated business question.

**Working in teams:** [Team size: X — confirm with your instructor]. The presentation is assessed as a team; your commit history is assessed individually — so push your own work under your own GitHub account.



``` actual Readme file starts here?```

# Singapore Jobs Analytics Data Product

## Overview

This project analyses more than 1 million Singapore job postings to provide interactive insights into salaries, hiring demand, competition and hiring trends.

The dashboard enables users to explore the Singapore labour market through dynamic filters and visualisations.

---

## Dataset

The dataset contains Singapore job postings with information including:

- job title
- company name
- employment type
- salary range
- experience requirements
- job categories
- number of applications
- number of views
- repost information

The original dataset contains approximately 1 million job postings.

---

## Project Structure

```
.
├── .vscode/
│   └── settings.json            # VS Code project settings
│
├── dashboard/
│   ├── app.py                   # Streamlit dashboard application
│   └── requirements.txt         # Python dependencies
│
├── .gitignore                   # Files excluded from Git tracking
├── README.md                    # Project documentation
└── main.ipynb                   # Data cleaning and preprocessing notebook
```

---

## Technologies Used

* Python
* Pandas
* NumPy
* Plotly
* Streamlit
* Jupyter Notebook

---

## How to Run the Project

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Install required packages

Run:

```bash
pip install -r dashboard/requirements.txt
```

### 3. Run the Streamlit dashboard

Run:

```bash
streamlit run dashboard/app.py
```

The dashboard will open in your browser.

---

## Dashboard Features

* KPI summary cards
* Salary analysis
* Hiring demand analysis
* Application analysis
* Hard-to-fill industry analysis
* Hiring trends over time
* Interactive filters
* Searchable job postings table

---

## Team Members

* Gary
* Shabeenah
* Mustafa
* Michael
* Wee Lee
* Belina


