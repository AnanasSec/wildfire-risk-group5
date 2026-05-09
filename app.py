import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px
import plotly.graph_objects as go

# ── Color palette ─────────────────────────────────────────
COLORS = {
    'primary':   '#E8702A',   # main orange
    'secondary': '#F5B88A',   # light orange
    'dark':      '#6B2412',   # dark red
    'light':     '#F5DECC',   # very light peach
    'teal':      '#2A9D8F',   # safe / teal
    'text':      '#2C2520',   # dark text
}

RISK_SCALE   = ['#FAF8F2', '#F5DECC', '#F5B88A', '#E8702A', '#6B2412']
CAUSE_COLORS = ['#6B2412', '#8B2E14', '#B03A1A', '#C04A1F',
                '#E8702A', '#F08C42', '#F5B88A', '#F5DECC']

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.title("Team 5")
st.sidebar.subheader("California Wildfire Housing Risk Analysis")

page = st.sidebar.radio(
    "Project Sections",
    [
        "1. Wildfire Trends Over Time",
        "2. County Wildfire Risk",
        "3. Seasonal Risk",
        "4. Wildfire Causes",
        "5. Housing Suitability Score"
    ]
)

# ── DB connection ─────────────────────────────────────────
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD_HERE",
    database="wildfire_db"
)

# ── Helper: apply consistent Plotly layout ────────────────
def apply_theme(fig):
    fig.update_layout(
        paper_bgcolor="#FAF8F2",
        plot_bgcolor="#FAF8F2",
        font_color=COLORS['text'],
        font_family="sans-serif",
        margin=dict(l=20, r=20, t=50, b=40),
    )
    fig.update_xaxes(gridcolor="#E8E0D5", linecolor="#C9C0B5")
    fig.update_yaxes(gridcolor="#E8E0D5", linecolor="#C9C0B5")
    return fig


# ═══════════════════════════════════════════════════════════
# PAGE 1 — Wildfire Trends Over Time
# ═══════════════════════════════════════════════════════════
if page == "1. Wildfire Trends Over Time":
    st.subheader("Problem Statement: How has wildfire activity (frequency and burned area) changed in California from 2000–2024?")

    query = """
    SELECT 
        Year,
        COUNT(*) AS fire_frequency,
        SUM(`Acres Burned`) AS total_burned_area
    FROM fire_perimeters
    WHERE Year BETWEEN 2000 AND 2024
    GROUP BY Year
    ORDER BY Year;
    """
    df = pd.read_sql(query, conn)

    st.divider()

    # Fire frequency line chart
    st.subheader("Fire Frequency Over Time")
    fig1 = px.line(df, x="Year", y="fire_frequency",
                   color_discrete_sequence=[COLORS['primary']],
                   labels={"fire_frequency": "Number of Fires", "Year": "Year"})
    fig1 = apply_theme(fig1)
    fig1.update_traces(line=dict(width=2.5))
    st.plotly_chart(fig1, use_container_width=True)

    # Burned area line chart
    st.subheader("Total Burned Area Over Time")
    fig2 = px.line(df, x="Year", y="total_burned_area",
                   color_discrete_sequence=[COLORS['dark']],
                   labels={"total_burned_area": "Acres Burned", "Year": "Year"})
    fig2 = apply_theme(fig2)
    fig2.update_traces(line=dict(width=2.5))
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("Key Insights")
        
    st.markdown(
    """
    <div style="background-color:#F5DECC; border-left:5px solid #E8702A;
    padding:15px; border-radius:5px; color:#2C2520;">
    Wildfire frequency generally increased over time.
    The year 2020 stands out as the most severe year by burned area,
    while 2024 had the highest number of recorded fires.
    </div>
    """,
    unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════
# PAGE 2 — County Wildfire Risk
# ═══════════════════════════════════════════════════════════
if page == "2. County Wildfire Risk":
    st.subheader("Problem Statement: Which California counties carry the highest wildfire risk?")

    county_query = """
    SELECT
        incident_county,
        COUNT(*) AS fire_frequency,
        SUM(incident_acres_burned) AS total_burned_area
    FROM fire_incidents
    WHERE 
        YEAR(incident_date_created) BETWEEN 2013 AND 2025
        AND incident_county IS NOT NULL
        AND incident_county <> ''
        AND incident_county NOT LIKE '%,%'
    GROUP BY incident_county
    ORDER BY total_burned_area DESC;
    """
    county_df = pd.read_sql(county_query, conn)

    st.divider()

    # Top 10 by burned area
    st.subheader("Top Counties by Total Burned Area")
    top_area = county_df.head(10)
    fig3 = px.bar(top_area, x="incident_county", y="total_burned_area",
                  color_discrete_sequence=[COLORS['primary']],
                  labels={"incident_county": "County",
                          "total_burned_area": "Acres Burned"})
    fig3 = apply_theme(fig3)
    st.plotly_chart(fig3, use_container_width=True)

    # Top 10 by frequency
    st.subheader("Top Counties by Fire Frequency")
    top_frequency = county_df.sort_values("fire_frequency", ascending=False).head(10)
    fig4 = px.bar(top_frequency, x="incident_county", y="fire_frequency",
                  color_discrete_sequence=[COLORS['dark']],
                  labels={"incident_county": "County",
                          "fire_frequency": "Number of Fires"})
    fig4 = apply_theme(fig4)
    st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    st.subheader("County Wildfire Risk Table")
    st.dataframe(county_df)

    st.subheader("Key Insights")
    

    st.markdown(
    """
    <div style="background-color:#F5DECC; border-left:5px solid #E8702A;
    padding:15px; border-radius:5px; color:#2C2520;">
    Counties with higher burned area and higher fire frequency carry greater wildfire risk.
    For this analysis, rows with missing counties and multi-county fire records were removed
    to keep county-level results clean and consistent.
    </div>
    """,
    unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════
# PAGE 3 — Seasonal Risk
# ═══════════════════════════════════════════════════════════
if page == "3. Seasonal Risk":
    st.subheader("Problem Statement: When during the year is wildfire risk concentrated?")

    heatmap_query = """
    SELECT 
        Year,
        MONTH(`Alarm Date`) AS fire_month,
        MONTHNAME(`Alarm Date`) AS month_name,
        COUNT(*) AS fire_frequency,
        SUM(`Acres Burned`) AS total_burned_area
    FROM fire_perimeters
    WHERE 
        Year BETWEEN 2013 AND 2025
        AND `Alarm Date` IS NOT NULL
    GROUP BY Year, fire_month, month_name
    ORDER BY Year, fire_month;
    """
    heatmap_df = pd.read_sql(heatmap_query, conn)

    MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }

    st.divider()

    # Heatmap
    pivot_df = heatmap_df.pivot_table(
        index="Year",
        columns="fire_month",
        values="total_burned_area",
        aggfunc="sum",
        fill_value=0
    ).rename(columns=month_names)

    st.subheader("Wildfire Burned Area Heatmap (Year vs Month)")
    fig5 = px.imshow(
        pivot_df,
        color_continuous_scale=RISK_SCALE,
        aspect="auto",
        labels=dict(color="Acres Burned")
    )
    fig5 = apply_theme(fig5)
    st.plotly_chart(fig5, use_container_width=True)

    st.divider()

    # Monthly aggregates
    monthly_risk = heatmap_df.groupby("fire_month", as_index=False).agg(
        total_fire_frequency=("fire_frequency", "sum"),
        total_burned_area=("total_burned_area", "sum")
    )
    monthly_risk["month_name"] = monthly_risk["fire_month"].map(month_names)
    monthly_risk = monthly_risk.sort_values("fire_month")

    # Burned area by month bar
    st.subheader("Total Burned Area by Month")
    fig6 = px.bar(monthly_risk, x="month_name", y="total_burned_area",
                  color_discrete_sequence=[COLORS['primary']],
                  category_orders={"month_name": MONTH_ORDER},
                  labels={"month_name": "Month",
                          "total_burned_area": "Acres Burned"})
    fig6 = apply_theme(fig6)
    st.plotly_chart(fig6, use_container_width=True)

    st.divider()

    # Frequency by month bar
    st.subheader("Fire Frequency by Month")
    fig7 = px.bar(monthly_risk, x="month_name", y="total_fire_frequency",
                  color_discrete_sequence=[COLORS['dark']],
                  category_orders={"month_name": MONTH_ORDER},
                  labels={"month_name": "Month",
                          "total_fire_frequency": "Number of Fires"})
    fig7 = apply_theme(fig7)
    st.plotly_chart(fig7, use_container_width=True)

    st.divider()
    st.subheader("Key Insights")
    
    st.markdown(
    """
    <div style="background-color:#F5DECC; border-left:5px solid #E8702A;
    padding:15px; border-radius:5px; color:#2C2520;">
    Wildfire risk is highly seasonal. Burned area and fire frequency are usually highest
    during late summer and early fall, especially from July through October.
    The heatmap shows how wildfire severity changes by month across different years.
    </div>
    """,
    unsafe_allow_html=True
)


# ═══════════════════════════════════════════════════════════
# PAGE 4 — Wildfire Causes
# ═══════════════════════════════════════════════════════════
if page == "4. Wildfire Causes":
    st.subheader("Problem Statement: What causes California wildfires — and is the risk preventable?")

    cause_query = """
    SELECT
        cl.cause_description,
        COUNT(*) AS fire_count
    FROM fire_perimeters fp
    JOIN cause_lookup cl ON fp.Cause = cl.cause_code
    WHERE fp.Year BETWEEN 2013 AND 2024
    GROUP BY cl.cause_description
    ORDER BY fire_count DESC;
    """
    cause_df = pd.read_sql(cause_query, conn)

    st.divider()

    # Top causes bar chart
    st.subheader("Top Causes of Wildfires")
    top_causes = cause_df.head(10)
    fig8 = px.bar(top_causes, x="cause_description", y="fire_count",
                  color_discrete_sequence=[COLORS['primary']],
                  labels={"cause_description": "Cause",
                          "fire_count": "Number of Fires"})
    fig8 = apply_theme(fig8)
    fig8.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig8, use_container_width=True)

    st.divider()

    # Pie chart (donut)
    st.subheader("Wildfire Causes Distribution")
    donut_causes = cause_df.head(8)
    fig9 = px.pie(donut_causes,
                  names="cause_description",
                  values="fire_count",
                  hole=0.5,
                  color_discrete_sequence=CAUSE_COLORS)
    fig9.update_traces(textinfo="percent+label")
    fig9 = apply_theme(fig9)
    st.plotly_chart(fig9, use_container_width=True)

    st.divider()
    st.subheader("Wildfire Cause Table")
    st.dataframe(cause_df)

    st.divider()
    st.subheader("Key Insights")
   
    st.markdown(
    """
    <div style="background-color:#F5DECC; border-left:5px solid #E8702A;
    padding:15px; border-radius:5px; color:#2C2520;">
    The chart shows the most common recorded wildfire causes in California.
    Human-related causes such as equipment use, campfires, vehicles, powerlines,
    and arson indicate that many wildfire risks may be preventable through better
    policy, regulation, and public awareness."
    </div>
    """,
    unsafe_allow_html=True
)


# ═══════════════════════════════════════════════════════════
# PAGE 5 — Housing Suitability Score
# ═══════════════════════════════════════════════════════════
if page == "5. Housing Suitability Score":
    import requests

    st.subheader("Problem Statement: Where should you buy based on wildfire risk across California counties?")

    map_query = """
    SELECT
        incident_county AS county,
        COUNT(*) AS fire_frequency,
        SUM(incident_acres_burned) AS total_burned_area
    FROM fire_incidents
    WHERE
        YEAR(incident_date_created) BETWEEN 2013 AND 2025
        AND incident_county IS NOT NULL
        AND incident_county <> ''
        AND incident_county NOT LIKE '%,%'
    GROUP BY incident_county
    ORDER BY fire_frequency DESC;
    """
    map_df = pd.read_sql(map_query, conn)

    st.divider()

    # Choropleth map
    geojson_url = "https://raw.githubusercontent.com/ucd-library/california-counties/master/geojson/california_counties.geojson"
    ca_counties = requests.get(geojson_url).json()
    map_df["county"] = map_df["county"].str.strip()


    # Create choropleth map
    fig10 = px.choropleth(
        map_df,
        geojson=ca_counties,
        locations="county",
        featureidkey="properties.name",
        color="fire_frequency",
        color_continuous_scale="Reds",
        hover_name="county",
        hover_data={
            "fire_frequency": True,
            "total_burned_area": True
        },
        labels={
            "fire_frequency": "Fire Count",
            "total_burned_area": "Burned Area"
        }
    )

    fig10.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig10.update_layout(
        title_text="California Housing Suitability (Wildfire Risk by County)",
        margin={"r": 0, "t": 50, "l": 0, "b": 0}
    )

    st.subheader("California County Wildfire Risk Map")
    st.plotly_chart(fig10, use_container_width=True)

    st.divider()


    # Top 10 bar chart
    st.subheader("Top 10 High-Risk Counties")
    top_10 = map_df.head(10)
    fig11 = px.bar(top_10, x="county", y="fire_frequency",
                   color_discrete_sequence=[COLORS['primary']],
                   labels={"county": "County",
                           "fire_frequency": "Number of Fires"})
    fig11 = apply_theme(fig11)
    st.plotly_chart(fig11, use_container_width=True)

    st.divider()

    # Top 5 riskiest & safest
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 Riskiest Counties")
        st.dataframe(map_df.head(5))
    with col2:
        st.subheader("Top 5 Safest Counties")
        st.dataframe(map_df.sort_values("fire_frequency", ascending=True).head(5))

    st.divider()
    st.subheader("All Counties Data")
    st.dataframe(map_df)

    st.divider()
    st.subheader("Key Insights")

    st.markdown(
    """
    <div style="background-color:#F5DECC; border-left:5px solid #E8702A;
    padding:15px; border-radius:5px; color:#2C2520;">
    Counties with darker shades on the map indicate higher wildfire frequency and risk.
    Top high-risk counties experience frequent wildfire incidents, while lower-risk counties
    may be more suitable for housing decisions. This visualization helps identify safer regions
    based on historical wildfire activity.
    </div>
    """,
    unsafe_allow_html=True
)
