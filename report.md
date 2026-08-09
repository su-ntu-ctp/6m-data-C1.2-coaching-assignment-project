# Singapore Job Market Intelligence Dashboard

## 1. Business Understanding

### Business Scenario

Many job seekers search for jobs by looking at individual job advertisements. However, this makes it difficult to understand the overall job market, such as which industries offer higher salaries, have stronger hiring demand, or attract more applications. Career advisors and workforce planners also need a broader view of the job market to support career planning and workforce decisions.

### Business Case

**Build a data product that provides insights into Singapore's job market using historical job postings.**

The purpose of this project is to transform raw job posting data into an interactive dashboard that helps users better understand Singapore's job market through data visualisation, filtering, and analysis.

### Target Users

The dashboard is intended for:

- Job seekers exploring career opportunities
- Career advisors supporting job seekers
- Workforce planners monitoring hiring trends

By presenting salary, hiring demand, applications, and hiring trends in an interactive dashboard, users can compare industries more easily and make better-informed decisions.

### Business Questions

The dashboard was designed to answer the following business questions:

1. Which industries offer the highest average salaries?
2. Which industries have the greatest hiring demand?
3. Which industries receive the most job applications?
4. Which industries are hardest to fill?
5. How has hiring changed over time?

---

## 2. Data Understanding

The project uses the **SGJobData** dataset, which contains approximately 1.05 million historical job postings in Singapore across 22 columns. The dataset provides a broad range of information for analysing salary levels, hiring demand, competition and hiring trends across different industries.

The dataset includes information such as:

- Company name
- Job title
- Industry category
- Employment type
- Position level
- Salary range
- Years of experience required
- Number of vacancies
- Job applications
- Job views
- Posting dates
- Repost information
- Job status

---

## 3. Data Preparation

More than one million job postings were cleaned and prepared through:

- Removing empty records with missing essential job information
- Removing duplicate postings
- Standardising company names by removing unnecessary suffixes (such as "PTE. LTD.") and fixing inconsistent formatting
- Cleaning job titles by removing extra spaces and applying consistent title casing
- Converting columns to appropriate data types (including dates, categories and text)
- Removing unrealistic salary records (including very low salaries, unusually high salaries and abnormal salary ranges)
- Removing job postings requiring 30 years or more of experience, as they represented approximately the top 0.01% of the data and were considered unrealistic.
- Checking repost consistency
- Saving the cleaned dataset for dashboard development

After the cleaning process, the dataset contained approximately 1.02 million job postings, retaining the large majority of the original records while removing records that could negatively affect the analysis.

These steps improved data quality, and ensured consistent and reliable analysis.

The cleaning process was designed to reduce the impact of missing, duplicated, inconsistent and unrealistic records while preserving as much useful information as possible for the dashboard.

---

## 4. Dashboard Development and Findings

The dashboard was developed using **Streamlit**, **Pandas** and **Plotly**. Users can filter job postings by salary, industry, employment type, position level, experience, posting period and job status. The dashboard updates automatically based on the selected filters.

It also provides an overview of the selected job market through key metrics and interactive visualisations, allowing users to compare different industries and job characteristics.

The dashboard addresses the five business questions through interactive charts showing:

- Average salary by industry
- Hiring demand based on total vacancies
- Number of job applications by industry
- Repost activity by industry
- Hiring trends over time

Additional breakdowns allow users to explore the distribution of job postings across different industries, employment types and position levels.

Users can also browse the filtered job postings in a searchable table, allowing them to move from high-level market insights to individual job listings and explore the underlying records in more detail.

### Key Business Findings

- **Legal, Risk Management** and **Banking & Finance** offer the highest average monthly salaries.
- Hiring demand remains strong across many industries, with consistent recruitment activity over time.
- Competition differs across industries, with some industries attracting far more applications than others.
- Repost activity also differs across industries. Industries with higher repost activity may indicate continued recruitment needs or difficulty filling certain positions, although reposts should be interpreted as an indicator rather than a direct measure of hiring difficulty.
- The dashboard allows users to interactively explore salary levels, hiring demand, competition and employment patterns to support better career and workforce decisions.

The findings should be interpreted based on the selected filters and the historical job-posting data used in the project. They provide an overview of patterns in the dataset rather than representing the entire Singapore labour market.

---

## Challenges and Learning

### Challenge

The SGJobData dataset contained several common data quality issues, including missing values, duplicate records, inconsistent text formatting, extra whitespace, and multiple category IDs stored within a single field. It also contained inconsistent salary values, incorrect data types, and inconsistent company names, all of which reduced the overall quality of the dataset. Considerable effort was required to clean and validate the data so that the analysis would be as accurate and reliable as possible for salary benchmarking, job market analysis, and workforce decision-making.

Another challenge was deciding which insights to include in the dashboard. As the dataset can be used for many different types of analysis, it was important to prioritise the most meaningful insights so that the dashboard remained clear, focused, and easy to use.

### What We Learned

This project showed that data cleaning is one of the most important stages of the data analytics process. High-quality and consistent data lead to more accurate analysis and more reliable insights. The project also provided hands-on experience using Pandas for data cleaning and analysis, Plotly for data visualisation, and Streamlit to build an interactive dashboard that presents information in a clear and user-friendly way.

Overall, the project demonstrated how raw job posting data can be transformed into a useful data product that supports better understanding of Singapore's job market and helps users make more informed career and workforce decisions.