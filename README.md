# ABI Admissions Dashboard

An interactive Streamlit dashboard for visualizing Acquired Brain Injury (ABI) admissions statistics across UK regions, with an automated data processing pipeline for transforming raw Excel files into analysis-ready datasets.

## Overview

This project consists of two main components:

1. **Data Processing Pipeline**: Automated scripts that extract, transform, and combine ABI admissions data from Excel files
2. **Interactive Dashboard**: Streamlit-based visualization tool for exploring the processed data

The system processes ABI admissions data from Excel files in the `raw_data/` folder, including:
- Regional England data (London, South West, East Midlands, West Midlands, etc.)
- UK-wide data (England, Scotland, Wales, Northern Ireland, and UK totals)

### Important Caveat

**Note**: The original Yorkshire and Humber Excel spreadsheets were missing header rows. These have been manually inserted before processing to ensure data consistency across all regions.

## Features

- **Interactive Visualizations**: Trend charts, regional comparisons, and heatmaps
- **Geographical Mapping**: NUTS1 boundary maps with choropleth visualization
- **Data Processing**: Automatically handles complex Excel formatting and extracts meaningful data
- **Regional Analysis**: Compare statistics across different UK regions
- **Temporal Analysis**: Track trends over financial years
- **Data Export**: Download filtered data as CSV files
- **Multiple Map Types**: Static matplotlib maps and interactive Folium maps

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. For geographical mapping functionality, install additional dependencies:
```bash
python install_geographical_deps.py
```

   Or manually install:
```bash
pip install geopandas matplotlib folium contextily shapely fiona pyproj
```

3. Ensure the Excel files are in the same directory as the dashboard files.

## Usage

### Basic ABI Admissions Dashboard

To visualize the processed ABI admissions data:

```bash
streamlit run abi_dashboard.py
```

### Enhanced Dashboard with Geographical Mapping

For the full experience with NUTS1 boundary maps:

```bash
streamlit run enhanced_abi_dashboard.py
```

The enhanced dashboard provides:
- Time series analysis of admissions trends
- Regional comparisons across UK regions
- **Geographical mapping with NUTS1 boundaries**
- **Interactive and static map visualizations**
- Injury type breakdowns (Head injuries, Stroke, Meningitis, etc.)
- Gender-based analysis
- Interactive filters for year range and regions
- Downloadable filtered datasets

### Full UK Dashboard (if available)

For the complete UK analysis:

```bash
streamlit run abi_dashboard.py
```

The dashboard will open in your web browser at `http://localhost:8501`.

### Dashboard Controls

- **Select Regions**: Choose which UK regions to include in visualizations
- **Select Primary Metric**: Choose the main metric for trend analysis
- **Select Metrics for Heatmap**: Choose multiple metrics for heatmap visualization
- **Select Year for Comparison**: Choose a specific year for regional comparison

### Visualizations

1. **Key Statistics**: Overview metrics including total records, regions covered, and years covered
2. **Trend Analysis**: Line charts showing how selected metrics change over time
3. **Regional Comparison**: Bar charts comparing regions for a specific year
4. **Regional Heatmap**: Heatmap showing multiple metrics across regions and years
5. **Raw Data Table**: Filtered data table with download capability

## Data Processing Pipeline

The project includes a three-stage automated data processing pipeline that transforms raw Excel files into analysis-ready CSV files:

### Stage 1: Excel Processing (`excel_processor.py`)

Extracts and transforms data from Excel files:
- Reads all Excel files from `raw_data/` folder
- Extracts the second sheet (regional data) from each file
- Removes the top 6 header rows
- Replaces 'Other disorders' text with standardized 'Other_disorders'
- Copies category labels (All ABI, Head injuries, Stroke, etc.) across relevant columns
- Concatenates 'Rate' with gender/total labels
- Adds '_Count' suffix to Female, Male, and Total columns
- Splits data by blank rows into separate year files (2006-07, 2007-08, etc.)
- Creates region-specific subfolders in `processed_data/` (e.g., `South_West/`, `London/`)

**Output**: Raw CSV files organized by region in `processed_data/[Region]/`

### Stage 2: CSV Processing (`csv_processor.py`)

Standardizes headers and adds metadata columns:
- Processes all CSV files within region subfolders
- Replaces spaces with underscores in headers
- Concatenates multi-row headers into single-row format
- Adds 'Regime' column (PCT, CCG, or ICB based on year)
- Adds 'FinancialYear' column
- Adds 'Organisation' column
- Removes formatting artifacts and cleans data
- Deletes redundant header rows

**Output**: Processed CSV files with standardized headers, overwriting originals in subfolders

### Stage 3: Data Combination (`csv_combiner.py`)

Combines year files and creates master datasets:
- Adds 'Region' column to identify data source
- Combines all year files within each region subfolder
- Creates regional combined files (e.g., `South_West.csv`, `London.csv`)
- Tests header consistency across files
- Combines all regional files into a master `England.csv` file
- Saves `England.csv` to `processed_data/` directory

**Output**: 
- Regional combined files in each subfolder
- Master `England.csv` file containing all regions and years

### Running the Pipeline

Execute the scripts in order:

```bash
# Step 1: Extract and transform Excel files
python excel_processor.py

# Step 2: Standardize CSV headers and add metadata
python csv_processor.py

# Step 3: Combine year files and create master dataset
python csv_combiner.py
```

### Pipeline Output Structure

```
processed_data/
├── England.csv                    # Master file with all regions
├── South_West/
│   ├── South_West.csv            # Regional combined file
│   ├── 2006_07.csv               # Individual year files
│   ├── 2007_08.csv
│   └── Regional_total.csv
├── London/
│   ├── London.csv
│   ├── 2006_07.csv
│   └── ...
└── [Other Regions]/
    └── ...
```

### Legacy Data Processor

The `data_processor.py` module provides additional data handling capabilities:
- Automatically detects header rows in non-standard Excel layouts
- Cleans and standardizes column names
- Converts numeric data appropriately
- Handles missing values and formatting inconsistencies

## File Structure

```
├── raw_data/                      # Source Excel files
│   ├── london-residents-abi-admissions.xlsx
│   ├── south-west-residents-abi-admissions.xlsx
│   ├── east-midlands-residents-abi-admissions.xlsx
│   └── ...
├── processed_data/                # Processed CSV files (generated)
│   ├── England.csv               # Master combined file
│   └── [Region]/                 # Region-specific subfolders
│       ├── [Region].csv          # Regional combined file
│       └── [Year].csv            # Individual year files
├── excel_processor.py            # Stage 1: Excel extraction and transformation
├── csv_processor.py              # Stage 2: CSV header standardization
├── csv_combiner.py               # Stage 3: Data combination
├── abi_dashboard.py              # Main Streamlit dashboard
├── data_processor.py             # Legacy data processing module
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Technical Details

- **Framework**: Streamlit for the web interface
- **Visualization**: Plotly for interactive charts
- **Data Processing**: Pandas for data manipulation
- **Excel Handling**: openpyxl for Excel file processing

## Notes

- The Excel files contain data in non-standard formats with headers scattered throughout
- The processor automatically handles these formatting challenges
- Data is cached for improved performance on subsequent loads
- All visualizations are interactive and responsive

## Troubleshooting

If you encounter issues:

1. Ensure all Excel files are present in the working directory
2. Check that all dependencies are installed: `pip install -r requirements.txt`
3. Verify the Excel files are not corrupted or password-protected
4. Check the console output for any data processing warnings

## Contributing

This dashboard is designed to be easily extensible. You can:
- Add new visualization types in the dashboard
- Modify the data processing logic for different Excel formats
- Add new metrics or filtering options
- Customize the styling and layout