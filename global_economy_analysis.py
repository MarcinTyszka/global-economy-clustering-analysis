import sys
import subprocess
import os
import webbrowser

def setup_environment():
    # Install required dependencies before importing them
    packages = ["pandas", "wbgapi", "folium", "geopandas", "scikit-learn", "branca"]
    print("Checking and installing required dependencies. This may take a moment...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + packages)
    print("Environment setup complete.")

setup_environment()

import pandas as pd
import wbgapi as wb
import folium
import geopandas as gpd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from branca.element import Template, MacroElement

def fetch_data():
    # Fetch geography data and economic indicators
    print("Fetching world geography data...")
    url = "https://raw.githubusercontent.com/datasets/geo-boundaries-world-110m/master/countries.geojson"
    world = gpd.read_file(url)
    world.columns = world.columns.str.lower()

    if 'iso_a3' not in world.columns:
        for col in ['id', 'adm0_a3', 'iso_3']:
            if col in world.columns:
                world = world.rename(columns={col: 'iso_a3'})
                break
    world = world[world['name'] != "Antarctica"]

    print("Fetching economic indicators...")
    indicators = {
        'NY.GDP.PCAP.CD': 'GDP_per_Capita',
        'FP.CPI.TOTL.ZG': 'CPI_Inflation',
        'BX.KLT.DINV.WD.GD.ZS': 'FDI_Inflow',
        'SL.UEM.TOTL.ZS': 'Unemployment_Rate'
    }
    
    data = wb.data.DataFrame(indicators.keys(), mrnev=1).reset_index()
    data = data.rename(columns=indicators).rename(columns={'economy': 'iso_a3'})
    
    return world, data, indicators

def process_and_cluster(world, data, indicators):
    # Merge datasets and apply KMeans clustering
    print("Merging datasets and applying clustering...")
    gdf = world.merge(data, on='iso_a3', how='inner')
    cluster_df = gdf.dropna(subset=list(indicators.values())).copy()

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(cluster_df[list(indicators.values())])

    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    cluster_df['Cluster_ID'] = kmeans.fit_predict(scaled_features)

    cluster_means = cluster_df.groupby('Cluster_ID')[list(indicators.values())].mean()

    gdf = gdf.merge(cluster_df[['iso_a3', 'Cluster_ID']], on='iso_a3', how='left')
    gdf['Cluster_ID'] = gdf['Cluster_ID'].fillna(-1).astype(int)
    
    return gdf, cluster_means

def generate_map(gdf, cluster_means):
    # Generate interactive map, save to HTML and open in browser
    print("Generating interactive map...")
    m = folium.Map(location=[20, 0], zoom_start=2, min_zoom=2, tiles="CartoDB positron", no_wrap=True)

    colors = {-1: 'gray', 0: '#e41a1c', 1: '#377eb8', 2: '#4daf4a', 3: '#984ea3', 4: '#ff7f00'}

    for cluster in sorted(gdf['Cluster_ID'].unique()):
        group_name = f"Cluster {cluster}" if cluster != -1 else "No Data"
        feature_group = folium.FeatureGroup(name=group_name).add_to(m)
        
        cluster_mask = gdf[gdf['Cluster_ID'] == cluster]
        folium.GeoJson(
            cluster_mask,
            style_function=lambda x, color=colors[cluster]: {
                'fillColor': color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['name', 'Cluster_ID', 'GDP_per_Capita', 'CPI_Inflation', 'FDI_Inflow', 'Unemployment_Rate'],
                aliases=['Country:', 'Cluster ID:', 'GDP:', 'Inflation:', 'FDI %:', 'Unemployment %:'],
                localize=True
            )
        ).add_to(feature_group)

    folium.LayerControl(collapsed=False).add_to(m)

    legend_html = f"""
    {{% macro html(this, kwargs) %}}
    <div style="
        position: fixed; 
        bottom: 50px; left: 50px; width: 320px; height: auto; 
        background-color: white; border:2px solid grey; z-index:9999; font-size:12px;
        padding: 10px;
        ">
        <b>Cluster Profiles (Averages)</b><br>
        <table style="width:100%; text-align: left; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid black;">
                <th>ID</th><th>GDP</th><th>Inf.</th><th>FDI</th><th>Unemp</th>
            </tr>
    """
    for idx, row in cluster_means.iterrows():
        legend_html += f"""
            <tr>
                <td style="color:{colors[idx]}; font-weight:bold;">{idx}</td>
                <td>${row['GDP_per_Capita']:,.0f}</td>
                <td>{row['CPI_Inflation']:.1f}%</td>
                <td>{row['FDI_Inflow']:.1f}%</td>
                <td>{row['Unemployment_Rate']:.1f}%</td>
            </tr>
        """
    legend_html += """
        </table>
        <small>* -1: Missing Data (Gray)</small>
    </div>
    {% endmacro %}
    """

    macro = MacroElement()
    macro._template = Template(legend_html)
    m.get_root().add_child(macro)

    output_file = "global_economy_clusters.html"
    m.save(output_file)
    
    print("Opening the map in the browser...")
    file_path = f"file://{os.path.abspath(output_file)}"
    webbrowser.open(file_path)

if __name__ == "__main__":
    world_gdf, eco_data, indicators_dict = fetch_data()
    merged_gdf, means = process_and_cluster(world_gdf, eco_data, indicators_dict)
    generate_map(merged_gdf, means)