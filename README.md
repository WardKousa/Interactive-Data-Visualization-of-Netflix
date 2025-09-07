# Netflix Data Analysis 
![Filters2](https://github.com/user-attachments/assets/f2b21017-ff5b-4fa0-8b42-4c69fe606924)


Explore Netflix's catalog through an interactive, multi-tab Streamlit dashboard. Analyze content types, release trends, ratings, top countries, directors, genres, durations, PCA clustering, and genre co-occurrence networks.

## Features
- **Multi-tab Streamlit app**  
- **Overview:** Movies vs TV Shows, Ratings Distribution  
- **Time Analysis:** Trends over years and months  
- **Top Countries / Directors / Genres:** Top 10 visualizations + averages  
- **Duration Analysis:** Movie lengths & TV seasons by director  
- **PCA Genre Clustering:** Visualize genre similarities  
- **Genre Co-Occurrence Network:** Interactive network graph of genre overlaps  
- **Interactive Filters:** By release year, content type, and countries  
- **Hover & Expand Info:** Click or hover to see detailed explanations for every chart  

## Two Versions
- **S3 + SQLite version:** Loads the dataset from a public AWS S3 bucket, transforms and queries locally using SQLite for efficient processing, enabling rich interactive visualizations.  
- **Local CSV version:** Loads `netflix_titles.csv` from the project root.

## Installation and Run

Clone the repo and (optionally) create a virtual environment:

```bash
git clone https://github.com/WardKousa/netflix-dashboard.git
cd netflix-dashboard
```

```Optional: create virtual environment
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

```Install dependencies
```pip install -r requirements.txt
```
