# app.py
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from itertools import combinations
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.decomposition import PCA


netflix_charts_info = {
    "1": {
        "what_i_did": "I took all Netflix titles and counted how many are Movies versus TV Shows.",
        "what_the_chart_shows": "Each slice of the pie represents the proportion of Movies and TV Shows in the dataset.",
        "what_i_found": "Movies make up about 70% of Netflix’s catalog, while TV shows only account for 30%.",
        "interpretation": "Netflix has historically been movie-heavy, with more than twice as many films as series. This suggests that while TV shows may dominate pop culture conversations, the platform’s foundation is still primarily built on movies.",
        "features": "Hover to see exact counts and percentages; click legend to hide/show categories."
    },
    "2": {
        "what_i_did": "I grouped Netflix titles by their content rating (like PG, R, TV-MA, etc.) and counted how many titles fall into each category.",
        "what_the_chart_shows": "Each slice represents one rating category, showing how common different ratings are across all titles.",
        "what_i_found": "The most common ratings are TV-MA (36%) and TV-14 (25%), followed by TV-PG (10%), R (9%), and PG-13 (5%). Everything else is under 5%.",
        "interpretation": "Despite Netflix’s reputation for mature, edgy content, the majority of titles actually fall in the “teen/family” safe zone (TV-14 and below make up ~40%). At the same time, over one-third of the catalog is TV-MA, reflecting a balance: Netflix caters both to family viewing and adult audiences, but skews a bit more toward the latter.",
        "features": "Hover to see counts and percentages; click legend to toggle ratings on/off."
    },
    "3": {
        "what_i_did": "I grouped titles by release year and type (Movie or TV Show), then counted how many of each type came out each year.",
        "what_the_chart_shows": "Each bar represents a year. The bar is split into stacked segments for Movies and TV Shows, showing their yearly distribution.",
        "what_i_found": "Netflix’s catalog grew very slowly from the 1950s to the early 2000s. Around 2005, movies ramped up significantly, and by 2015 growth exploded, peaking in 2018–2019 with over 1,500 titles. After that, total additions declined, especially for movies. TV shows, which started much later, also peaked around 2018 but declined more gently.",
        "interpretation": "Netflix hit a “boom” phase around 2015–2019, adding titles aggressively to build its library. The sharp decline afterward may reflect a pivot: instead of maximizing quantity, Netflix began curating more carefully, possibly due to licensing issues and competition. The relative stability of TV shows compared to movies suggests a shift in focus toward serial content during this period.",
        "features": "Hover to see exact counts; toggle Movies or TV Shows from the legend to focus on one category."
    },
    "4": {
        "what_i_did": "I used the `date_added` field to count how many titles Netflix added over time, grouped by month.",
        "what_the_chart_shows": "The line represents how many titles were added to Netflix each month, showing peaks and trends in content acquisition.",
        "what_i_found": "Content additions were steady until 2015, after which Netflix sharply increased yearly releases. Growth plateaued around 2017–2018, then declined.",
        "interpretation": "This trend reflects Netflix’s transition from “building a catalog” to “maintaining one.” After an initial period of rapid expansion, Netflix may have shifted resources toward original productions and quality control, explaining the leveling-off.",
        "features": "Hover to see exact counts per month; zoom and pan across the timeline."
    },
    "5": {
        "what_i_did": "I grouped titles by release year and rating, then counted how many titles had each rating in each year.",
        "what_the_chart_shows": "Each line corresponds to a content rating (e.g., TV-MA, PG-13). It shows how that rating’s popularity changed over time.",
        "what_i_found": "All ratings categories grew sharply around 2015, but peaked around 2018 and then declined. TV-14 rose early, but TV-MA eventually became dominant, peaking at over 500 titles. Other categories (PG, R, etc.) never reached the same scale.",
        "interpretation": "Netflix’s early growth leaned family-friendly (TV-14), but the long-term shift is toward adult-oriented TV-MA content. This aligns with Netflix’s reputation for edgy original programming and may reflect higher retention from mature series compared to family titles.",
        "features": "Hover to see yearly counts per rating; click legend to show/hide ratings and compare trends."
    },
    "6": {
        "what_i_did": "I counted how many titles were produced in each country and selected the top 10 most frequent.",
        "what_the_chart_shows": "Each bar represents one country, with bar length showing how many Netflix titles came from that country.",
        "what_i_found": "The U.S. dominates Netflix’s catalog with over 3,600 titles. The U.K. follows with ~750, Canada (~450), France (~400), Japan (~300), and India (~100). The average country contributes ~80 titles.",
        "interpretation": "Netflix is overwhelmingly U.S.-centric, but its expansion strategy clearly emphasizes English-speaking countries first, with selective investments in other markets. Japan and India show Netflix’s global ambitions, though they remain far behind the U.S. and Europe in volume.",
        "features": "Hover to see counts; bars are sorted for easy comparison."
    },
    "7": {
        "what_i_did": "I counted how many titles each director was credited for and selected the top 10.",
        "what_the_chart_shows": "Each bar represents a director, with bar length showing the number of titles they directed.",
        "what_i_found": "Most directors on Netflix only have about one title. But a few dominate: Rajiv Chilaka (22 titles), Jan Suter (21), Raul Campos (18), Marcus Raboy & Suhas Kadav (16), Cathy Garcia Molina (13).",
        "interpretation": "Netflix content is highly fragmented across thousands of directors, but a few prolific names (many tied to specific regional industries like India or Mexico) contribute disproportionately. This shows Netflix’s strategy of partnering with certain “high-output” creators in emerging markets.",
        "features": "Hover to see counts; sorted by number of titles for clarity."
    },
    "8": {
        "what_i_did": "I split titles into genres and counted how many times each genre appeared, then picked the 10 most common.",
        "what_the_chart_shows": "Each bar represents one genre, with bar length showing how many titles belong to that genre.",
        "what_i_found": "International Movies lead (2,700+), followed by Dramas (2,400+), Comedies (1,600+), and International TV Shows (1,300+). Other genres like Documentaries, Action & Adventure, Independent Movies, Children & Family, and Romantic Movies range from ~600–850 each.",
        "interpretation": "Netflix’s library heavily favors international content and drama — likely because these genres travel well across cultures. Comedy and action are also major pillars, but niche categories (like romance or children’s movies) remain secondary.",
        "features": "Hover to see counts; color-coded bars make genres easy to distinguish."
    },
    "9": {
        "what_i_did": "For Movies only, I converted their duration into minutes and calculated each director’s average runtime. I then selected the top 15.",
        "what_the_chart_shows": "Each bar represents a director, with bar length showing their average movie runtime.",
        "what_i_found": "The average Netflix movie runs ~100 minutes. But some directors massively exceed that: Will Eisenberg (253 min avg), Scott McAboy, Joe Menendez, Pawan Kirpalani (~230 min), and the rest of the top 15 all average above 180 min.",
        "interpretation": "While most Netflix films are standard feature length, some directors specialize in unusually long projects — possibly reflecting specific genres (epics, multi-part films, or extended documentary features). This points to experimentation at the fringes of the catalog.",
        "features": "Hover to see exact average durations; sorted from longest to shortest for comparison."
    },
    "10": {
        "what_i_did": "For TV Shows only, I converted the “duration” field into number of seasons and calculated each director’s average. I then selected the top 15.",
        "what_the_chart_shows": "Each bar represents a director, with bar length showing their average number of seasons per show.",
        "what_i_found": "The average Netflix TV show lasts only 1.6 seasons. But outliers like Jérémy Clapin (15 seasons) and a handful of others (Upi Avianto, Andrew Niccol, Kongkiat Komesir) last 7–9 seasons.",
        "interpretation": "Most Netflix shows are very short-lived, with few reaching multi-season longevity. This supports the view that Netflix frequently experiments with series but cancels quickly if traction isn’t achieved. A small handful of long-running series stand out as exceptions.",
        "features": "Hover to see averages; sorted list makes comparison easier."
    },
    "11": {
        "what_i_did": "I took all of Netflix’s titles and represented them by their genres (e.g., comedy, drama, horror, etc.). That makes each title a big list of 0/1 values (“is this title in this genre?”). Since that data is very high-dimensional, I used a technique called PCA (Principal Component Analysis) to compress it down into just 2 dimensions, while keeping as much of the structure as possible.",
        "what_the_chart_shows": "Each dot is a Netflix title. Dots that are close together share similar genre profiles. I then colored the dots by whether the title is a Movie or a TV Show.",
        "what_i_found": "TV Shows tend to cluster together tightly. This suggests Netflix TV shows often follow a fairly narrow set of genre combinations (for example, a lot of shows may fall into predictable mixes like drama + comedy or action + thriller). Movies are much more scattered. This means Netflix movies cover a broader and more diverse range of genres — you can find everything from rom-coms to horror to documentaries.",
        "interpretation": "TV shows on Netflix are less experimental in genre (maybe to ensure long-term engagement), while movies are more varied and unpredictable.",
        "features": "Hover over dots to see title and details; zoom and pan around clusters."
    },
    "12": {
        "what_i_did": "I built a network where each node is a genre. If two genres appear together in the same title, they are connected by an edge. Edge thickness reflects how often the genres co-occur. Node size reflects how many titles belong to that genre.",
        "what_the_chart_shows": "The network shows how genres overlap. Larger nodes mean more titles in that genre, and thicker edges mean those two genres often appear together.",
        "what_i_found": "Genres like International Movies and Dramas dominate the network with the most connections to other genres. Comedy is also highly interconnected. By contrast, niches like British TV, Docuseries, or Stand-Up Comedy have very few connections.",
        "interpretation": "Netflix’s catalog revolves around broad, versatile genres (International, Drama, Comedy) that combine easily with others. Niche genres remain siloed with fewer overlaps, suggesting either a smaller catalog base or untapped opportunities. This could reflect where Netflix sees mainstream vs. niche audience value.",
        "features": "Hover over nodes to see genre names; hover over edges to see co-occurrence counts; zoom and pan; legend allows selection of genres (if dropdown is enabled)."
    }
}


# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(page_title="Netflix Dashboard", layout="wide")
st.title("📊 Netflix Data Analysis Dashboard")

# ------------------------
# LOAD DATA
# ------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\ward\Documents\projects\netflix\netflix_titles.csv")
    # Fix duration column
    df['duration_num'] = df['duration'].str.extract(r'(\d+)').astype(float)
    # Clean date_added
    df['date_added'] = pd.to_datetime(df['date_added'].astype(str).str.strip(), errors='coerce')
    df['rating'] = df['rating'].fillna('Unknown')
    return df

df = load_data()

st.sidebar.header("Filters")

# ------------------------
# SIDEBAR FILTERS
# ------------------------
# Year filter
year_min = int(df['release_year'].min())
year_max = int(df['release_year'].max())
years = st.sidebar.slider("Select Release Year Range", year_min, year_max, (year_min, year_max))

# Content type filter
content_type = st.sidebar.multiselect("Select Content Type", ["Movie", "TV Show"], default=["Movie","TV Show"])

# Country filter
all_countries = df['country'].dropna().str.split(',', expand=True).stack().str.strip().unique()
selected_countries = st.sidebar.multiselect("Select Production Countries (optional)", all_countries)

# Apply filters
df_filtered = df[df['release_year'].between(years[0], years[1])]
df_filtered = df_filtered[df_filtered['type'].isin(content_type)]
if selected_countries:
    df_filtered = df_filtered[df_filtered['country'].dropna().str.contains('|'.join(selected_countries))]

# ------------------------
# SQL EXAMPLE
# ------------------------
st.subheader("Sample SQL Query on Netflix Data")
# Create SQLite DB in memory
conn = sqlite3.connect(":memory:")
df.to_sql("netflix", conn, if_exists="replace", index=False)
cursor = conn.cursor()
cursor.execute("SELECT title, type, release_year FROM netflix LIMIT 5;")
rows = cursor.fetchall()
st.table(rows)
conn.close()

# ------------------------
# TABS FOR PLOTS
# ------------------------
tabs = st.tabs([
    "Overview", "Time Analysis", "Top Countries/Directors/Genres",
    "Duration Analysis", "PCA Genre Clustering", "Genre Co-Occurrence"
])

# ------------------------
# TAB 1: Overview
# ------------------------
with tabs[0]:
#Movies and TV show pie chart
    st.subheader("Movies vs TV Shows")
    type_counts = df_filtered['type'].value_counts()
    fig = px.pie(values=type_counts.values, names=type_counts.index, title="Movies vs TV Shows")
    st.plotly_chart(fig, use_container_width=True)
    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["1"]  # 1 = the first plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)

#Distribution of age ratings Pie Chart
    st.subheader("Distribution of Ratings")
    rating_counts = df_filtered['rating'].value_counts()
    fig = px.pie(values=rating_counts.values, names=rating_counts.index, title="Distribution of Ratings")
    st.plotly_chart(fig, use_container_width=True)
    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["2"]  # 2 for the second plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)

# ------------------------
# TAB 2: Time Analysis
# ------------------------
with tabs[1]:

#MOVIES vs TV SHOWS Over Time
    st.subheader("Movies vs TV Shows Over Time")
    type_year = df_filtered.groupby(['release_year','type']).size().reset_index(name='count')
    fig = px.bar(type_year, x='release_year', y='count', color='type',
                 title='Movies vs TV Shows per Year', barmode='stack',
                 labels={'release_year':'Year', 'count':'Number of Titles'})
    st.plotly_chart(fig, use_container_width=True)
    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["3"]  # 3 for the third plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)

#Content Added Per MOnth
    st.subheader("Content Added Over Time (Monthly)")
    df_valid = df_filtered.dropna(subset=['date_added'])
    added_counts = df_valid.groupby(df_valid['date_added'].dt.to_period('M')).size()
    fig = px.line(x=added_counts.index.astype(str), y=added_counts.values,
                  labels={'x':'Month','y':'Number of Titles added that month'}, title='Number of Content added each month')
    st.plotly_chart(fig, use_container_width=True)
    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["4"]  # 4 for the fourth plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)

# Content Ratings Trends Over Years
    st.subheader("Content Ratings Trends Over Years")

    # Filter by selected years
    df_filtered_year = df_filtered[(df_filtered['release_year'] >= years[0]) &
                                   (df_filtered['release_year'] <= years[1])]

    # Group data
    rating_year = df_filtered_year.groupby(['release_year', 'rating']).size().reset_index(name='count')

    # Define a fixed color map for ratings
    unique_ratings = df['rating'].fillna('Unknown').unique()
    colors = px.colors.qualitative.Plotly  # or any palette you like
    color_map = {rating: colors[i % len(colors)] for i, rating in enumerate(sorted(unique_ratings))}

    # Create the line chart with fixed colors
    fig = px.line(
        rating_year,
        x='release_year',
        y='count',
        color='rating',
        title='Content Ratings Over Time',
        color_discrete_map=color_map
    )

    st.plotly_chart(fig, use_container_width=True)
    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["5"]  # 5 for the fifth plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)

# ------------------------
# TAB 3: Top Countries / Directors / Genres
# ------------------------
with tabs[2]:
# Top 10 Countries
    st.subheader("Top 10 Countries Producing Netflix Titles")
    countries = df_filtered['country'].dropna().str.split(',', expand=True).stack().str.strip()
    top_countries = countries.value_counts().head(10)
    avg_countries = countries.value_counts().mean()  # Average across all countries
    top_countries_with_avg = pd.concat([top_countries, pd.Series({'Average': avg_countries})])

    # Colors: original Pastel for top 10, gray for Average
    colors_countries = [px.colors.qualitative.Pastel[i] for i in range(len(top_countries))] + ['gray']

    # Checkbox to show/hide average line
    show_avg_line_countries = st.checkbox("Show Average Line (Countries)", value=True)

    fig = px.bar(
        x=top_countries_with_avg.index,
        y=top_countries_with_avg.values,
        labels={'x': 'Country', 'y': 'Number of Titles'},
        title="Top 10 Countries Producing Netflix Titles + Average",
        color=top_countries_with_avg.index,
        color_discrete_sequence=colors_countries
    )

    # Add the dashed line only if checkbox is selected
    if show_avg_line_countries:
        fig.add_hline(y=avg_countries, line_dash="dash", line_color="white", line_width=3)

    st.plotly_chart(fig, use_container_width=True)

    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["6"]  # 6 for the sixth plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)



# Top 10 Directors
    st.subheader("Top 10 Directors")
    directors = df_filtered['director'].dropna().str.split(',', expand=True).stack().str.strip()
    top_directors = directors.value_counts().head(10)
    avg_directors = directors.value_counts().mean()
    top_directors_with_avg = pd.concat([top_directors, pd.Series({'Average': avg_directors})])

    # Colors: original Vivid for top 10, gray for Average
    colors_directors = [px.colors.qualitative.Vivid[i] for i in range(len(top_directors))] + ['gray']

    # Checkbox to show/hide average line
    show_avg_line_directors = st.checkbox("Show Average Line (Directors)", value=True)

    fig = px.bar(
        x=top_directors_with_avg.index,
        y=top_directors_with_avg.values,
        labels={'x': 'Director', 'y': 'Number of Titles'},
        title="Top 10 Directors + Average",
        color=top_directors_with_avg.index,
        color_discrete_sequence=colors_directors
    )

    if show_avg_line_directors:
        fig.add_hline(y=avg_directors, line_dash="dash", line_color="white", line_width=3)

    st.plotly_chart(fig, use_container_width=True)

    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["7"]  # 7 for the seventh plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)

# Top 10 Genres
    st.subheader("Top 10 Genres")
    genres = df_filtered['listed_in'].dropna().str.split(',', expand=True).stack().str.strip()
    top_genres = genres.value_counts().head(10)
    avg_genres = genres.value_counts().mean()
    top_genres_with_avg = pd.concat([top_genres, pd.Series({'Average': avg_genres})])

    # Option to show/hide average line
    show_avg_line = st.checkbox("Show Average Line", value=True)

    # Use D3 colors for top 10, magenta for Independent Movies
    colors_genres = px.colors.qualitative.D3[:len(top_genres)]
    colors_genres = [("magenta" if genre == "Independent Movies" else color)
                     for genre, color in zip(top_genres.index, colors_genres)]
    colors_genres.append("gray")  # Average bar

    fig = px.bar(
        x=top_genres_with_avg.index,
        y=top_genres_with_avg.values,
        labels={'x': 'Genre', 'y': 'Number of Titles'},
        title="Top 10 Genres + Average",
        color=top_genres_with_avg.index,
        color_discrete_sequence=colors_genres
    )

    # Add the average line only if checkbox is checked
    if show_avg_line:
        fig.add_hline(y=avg_genres, line_dash="dash", line_color="white", line_width=3)

    st.plotly_chart(fig, use_container_width=True)

    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["8"]  # 8 for the eight plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)

# ------------------------
# TAB 4: Duration Analysis
# ------------------------
with tabs[3]:
    #assigning values of directors and their works durations
    df_director = df_filtered.dropna(subset=['director','duration_num','type']).copy()
    df_director['director'] = df_director['director'].str.split(',').explode('director').str.strip()
    # ------------------------

    # Top 15 Movie Directors
    st.subheader("Top 15 Movie Directors by Average Movie Duration")
    movies_dir = df_director[df_director['type']=='Movie']
    avg_duration_movies = movies_dir.groupby('director')['duration_num'].mean().sort_values(ascending=False).head(15).reset_index()
    overall_avg_movie_duration = movies_dir['duration_num'].mean()

    avg_duration_movies_with_avg = pd.concat([
        avg_duration_movies.set_index('director')['duration_num'],
        pd.Series({'Average': overall_avg_movie_duration})
    ]).reset_index()
    avg_duration_movies_with_avg.columns = ['director','duration_num']

    # All bars same color except Average bar
    bar_color = "steelblue"
    colors_movies = [bar_color]*len(avg_duration_movies) + ["gray"]

    # Checkbox to show/hide average line
    show_avg_line_movies = st.checkbox("Show Average Line (Movies)", value=True)

    fig = px.bar(
        avg_duration_movies_with_avg,
        x='duration_num',
        y='director',
        orientation='h',
        labels={'duration_num':'Average Movie Duration (min)','director':'Director'},
        title="Top 15 Movie Directors + Overall Average",
        color=avg_duration_movies_with_avg['director'],
        color_discrete_sequence=colors_movies
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})

    if show_avg_line_movies:
        fig.add_vline(x=overall_avg_movie_duration, line_dash="dash", line_color="white", line_width=3)

    st.plotly_chart(fig, use_container_width=True)

    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["9"]  # 9 for the ninth plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)


    # Top 15 TV Show Directors
    st.subheader("Top 15 TV Show Directors by Average Number of Seasons")
    tv_dir = df_director[df_director['type']=='TV Show']
    avg_duration_tv = tv_dir.groupby('director')['duration_num'].mean().sort_values(ascending=False).head(15).reset_index()
    overall_avg_tv_duration = tv_dir['duration_num'].mean()

    avg_duration_tv_with_avg = pd.concat([
        avg_duration_tv.set_index('director')['duration_num'],
        pd.Series({'Average': overall_avg_tv_duration})
    ]).reset_index()
    avg_duration_tv_with_avg.columns = ['director','duration_num']

    # All bars same color except Average bar
    colors_tv = [bar_color]*len(avg_duration_tv) + ["gray"]

    # Checkbox to show/hide average line
    show_avg_line_tv = st.checkbox("Show Average Line (TV Shows)", value=True)

    fig = px.bar(
        avg_duration_tv_with_avg,
        x='duration_num',
        y='director',
        orientation='h',
        labels={'duration_num':'Average TV Show Duration (seasons)','director':'Director'},
        title="Top 15 TV Show Directors + Overall Average",
        color=avg_duration_tv_with_avg['director'],
        color_discrete_sequence=colors_tv
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})

    if show_avg_line_tv:
        fig.add_vline(x=overall_avg_tv_duration, line_dash="dash", line_color="white", line_width=3)

    st.plotly_chart(fig, use_container_width=True)
    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["10"]  # 10 for the tenth plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)
# ------------------------
# TAB 5: PCA Genre Clustering
# ------------------------
with tabs[4]:
    #PCA CLuster genre graph thingy
    st.subheader("PCA Clustering of Genres")
    df_pca = df_filtered.dropna(subset=['listed_in']).copy()
    df_pca['genres_list'] = df_pca['listed_in'].str.split(', ')
    mlb = MultiLabelBinarizer()
    genre_encoded = mlb.fit_transform(df_pca['genres_list'])
    genre_df = pd.DataFrame(genre_encoded, columns=mlb.classes_)
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(genre_df)
    pca_df = pd.DataFrame(pca_result, columns=['PCA1','PCA2'])
    pca_df['type'] = df_pca['type'].values
    fig = px.scatter(pca_df, x='PCA1', y='PCA2', color='type', title='PCA Clustering of Genres')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    **Explanation:** Each dot represents a title. Dots close together share similar genre combinations.
    TV Shows cluster tightly (predictable genres), Movies are more spread out (diverse genres).
    """)
    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["11"]  # 11 for the eleventh plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)
# ------------------------
# TAB 6: Genre Co-Occurrence Network
# ------------------------
with tabs[5]:

    #CO occurence network
    st.subheader("Genre Co-occurence network")

    # Preprocess genres
    df_exp = df.dropna(subset=['listed_in']).copy()
    df_exp['genres_list'] = df_exp['listed_in'].str.split(', ')

    # Count co-occurrences
    co_counts = {}
    for genres in df_exp['genres_list']:
        for g1, g2 in combinations(genres, 2):
            pair = tuple(sorted([g1, g2]))
            co_counts[pair] = co_counts.get(pair, 0) + 1

    # Create NetworkX graph
    G = nx.Graph()
    for (g1, g2), w in co_counts.items():
        G.add_edge(g1, g2, weight=w)

    # Node positions (circular layout)
    pos = nx.circular_layout(G)
    for k in pos:
        pos[k] = pos[k] * 1.2  # stretch for clarity

    # --- Swap specific nodes ---
    swap_pairs = [
        ('Drama', 'Anime Series'),
        ('Independent Movies', 'LGBTQ Movies'),
        ('Anime Series', 'International Movies')  # new requested swap
    ]
    for n1, n2 in swap_pairs:
        if n1 in pos and n2 in pos:
            pos[n1], pos[n2] = pos[n2], pos[n1]

    # Edge traces
    edge_traces = []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_traces.append(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            line=dict(width=G[u][v]['weight']/40, color='gray'),
            hoverinfo='text',
            text=f"{u} ↔ {v} (weight: {G[u][v]['weight']})",
            mode='lines'
        ))

    # Node trace
    genres = list(G.nodes())
    colors = px.colors.qualitative.Plotly  # color palette
    genre_color_map = {genre: colors[i % len(colors)] for i, genre in enumerate(genres)}

    node_trace = go.Scatter(
        x=[pos[n][0] for n in G.nodes()],
        y=[pos[n][1] for n in G.nodes()],
        mode='markers+text',
        text=list(G.nodes()),
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            size=30,
            color=[genre_color_map[n] for n in G.nodes()],
            line=dict(width=2, color='black')
        )
    )

    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        title="Netflix Genre Co-Occurrence Network",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    st.plotly_chart(fig, use_container_width=True)
    # the extra info
    with st.expander("❓", expanded=False):
        plot_info = netflix_charts_info["12"]  # 12 for the twelvth plot
        st.markdown(f"""
        **What I did:** {plot_info['what_i_did']}  
        **What the chart shows:** {plot_info['what_the_chart_shows']}  
        **What I found:** {plot_info['what_i_found']}  
        **Interpretation:** {plot_info['interpretation']}  
        **Features:** {plot_info['features']}
        """)
