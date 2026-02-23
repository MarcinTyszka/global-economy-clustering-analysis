# Global Economy Clustering Analysis

This project analyzes the global macroeconomic landscape by clustering countries based on key economic indicators. It automates data acquisition, applies machine learning for grouping, and generates a responsive, interactive map. 

The script is designed for a "zero-setup" experience: it automatically installs required dependencies, processes the data, and opens the final visualization in your default web browser.

## Features

* Automated Data Fetching: Integrates with the World Bank API (`wbgapi`) to pull real-time data and uses public GeoJSON sources for geographical boundaries.
* Key Indicators Analyzed:
  * GDP per Capita
  * CPI Inflation
  * Foreign Direct Investment (FDI) Inflow
  * Unemployment Rate
* Machine Learning: Standardizes the dataset and applies K-Means clustering (Scikit-Learn) to group countries with similar economic profiles.
* Interactive Visualization: Creates a Folium map with color-coded clusters, detailed tooltips, and a custom HTML legend showing cluster averages.
* Zero-Setup Execution: The script verifies and installs missing Python packages automatically upon execution.

## Technology Stack

* Language: Python 3
* Data Processing: Pandas, GeoPandas
* Machine Learning: Scikit-Learn
* Visualization: Folium, Branca
* External APIs: World Bank API

## How to Run

1. Run the main script:

```bash
python global_economy_analysis.py
```

The script will automatically install any missing libraries, download the latest data, perform the clustering analysis, generate the global_economy_clusters.html file, and open it in your browser.