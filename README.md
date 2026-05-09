# Wildfire Risk and Fire-Pattern Analytics System in California

This project analyzes historical wildfire data from CAL FIRE to help identify 
safer counties for homebuyers in California. Using 25 years of fire records, 
we built an interactive dashboard that visualizes wildfire trends, seasonal 
patterns, causes, and county-level risk across the state.

**Group 5 | Database Project**

---

## Project Setup Steps

### 1. Download the Project Files

- Go to the shared Google Drive link
- Download the folder and extract the ZIP file

### 2. Open the Project

- Open the project folder in VS Code
- Open a terminal and install dependencies:
```python
pip install streamlit pandas pymysql matplotlib plotly
```

### 3. MySQL Setup

Open MySQL Workbench and run:

```sql
CREATE DATABASE wildfire_db;
USE wildfire_db;
```

### 4. Import the Datasets

We have 3 types of files in this project:

| Type | Format | Description |
|---|---|---|
| `pre_dataset` | CSV | Raw data — downloaded as-is, no cleaning |
| `post_dataset` | CSV | Cleaned data — used for MySQL and analysis |
| `clean_dataset` | Python | Cleaning scripts — removes columns, fixes missing values |

**Import post_dataset2 as `fire_incidents`:**

- Right-click on `wildfire_db` in the left panel
- Click **Table Data Import Wizard**
- Select `post_dataset2.csv`
- Set table name to `fire_incidents`
- Click Next → Next → Done

Verify import:
```sql
SELECT * FROM fire_incidents;
```

**Import post_dataset3 as `fire_perimeters`:**

- Same steps as above
- Select `post_dataset3.csv`
- Set table name to `fire_perimeters`
- Click Next → Next → Done

Verify import:
```sql
SELECT * FROM fire_perimeters;
```

### 5. Create the Cause Lookup Table

Run this SQL in MySQL Workbench:

```sql
CREATE TABLE cause_lookup (
    cause_code INT PRIMARY KEY,
    cause_description VARCHAR(100),
    cause_category VARCHAR(20)
);

INSERT INTO cause_lookup VALUES
(1,  'Lightning',                 'Natural'),
(2,  'Equipment Use',             'Human'),
(3,  'Smoking',                   'Human'),
(4,  'Campfire',                  'Human'),
(5,  'Debris',                    'Human'),
(6,  'Railroad',                  'Human'),
(7,  'Arson',                     'Human'),
(8,  'Playing with fire',         'Human'),
(9,  'Miscellaneous',             'Human'),
(10, 'Vehicle',                   'Human'),
(11, 'Powerline',                 'Human'),
(12, 'Firefighter Training',      'Human'),
(13, 'Non-Firefighter Training',  'Human'),
(14, 'Unknown/Unidentified',      'Unknown'),
(15, 'Structure',                 'Human'),
(16, 'Aircraft',                  'Human'),
(17, 'Volcanic',                  'Natural'),
(18, 'Escaped Prescribed Burn',   'Human'),
(19, 'Illegal Alien Campfire',    'Human');
```

### 6. Update the Database Password

Open `app.py` in VS Code and update your MySQL password before running:

```python
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="YOUR PASSWORD",   # ← change this
    database="wildfire_db"
)
```

### 7. Run the Dashboard

In the terminal:
```python
streamlit run app.py
```

The dashboard will open in your browser. Use the left sidebar to navigate between the 5 project sections.


