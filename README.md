# Netflix Data Analysis Dashboard
Video demo coming very soon!  

Explore Netflix's catalog through an interactive, multi-tab Streamlit dashboard. Analyze content types, release trends, ratings, top countries, directors, genres, durations, PCA clustering, and genre co-occurrence networks.

## Features
- **Multi-tab Streamlit app**
  - Overview: Movies vs TV Shows, Ratings Distribution
  - Time Analysis: Trends over years and months
  - Top Countries/Directors/Genres: Top 10 visualizations + averages
  - Duration Analysis: Movie lengths & TV seasons by director
  - PCA Genre Clustering: Visualize genre similarities
  - Genre Co-Occurrence Network: Interactive network graph of genre overlaps
- **Interactive Filters:** by release year, content type, and countries
- **Hover & Expand Info:** Click or hover to see detailed explanations for every chart
- **Two Versions:**  
  1. **S3 version:** loads the dataset automatically from a public S3 bucket  
  2. **Local CSV version:** loads `netflix_titles.csv` from project root

## Installation and Run

### Clone the repo and (optionally) create a virtual environment:
```bash
git clone https://github.com/yourusername/netflix-dashboard.git
cd netflix-dashboard
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```
Install dependencies```
pip install -r requirements.txt```

Run the app```
streamlit run app.py```

Local CSV Version:
Place netflix_titles.csv in the project root.

Run the app as usual```
streamlit run app.py```
