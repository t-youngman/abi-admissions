# ABI Admissions Dashboard

An interactive Streamlit dashboard for visualizing Acquired Brain Injury (ABI) admissions statistics across England regions and organisations, with an automated data processing pipeline for transforming raw Excel files into analysis-ready datasets.

## Overview

This project consists of two main components:

1. **Data Processing Pipeline**: Automated scripts that extract, transform, and combine ABI admissions data from Excel files
2. **Interactive Dashboard**: Streamlit-based visualization tool for exploring the processed data at both regional and organisational levels

The system processes ABI admissions data from Excel files in the `england_data/` folder, covering all England regions:
- East, East Midlands, London, North East, North West
- South East, South West, West Midlands, Yorkshire and Humberside

### Important Caveat

**Note**: The original Yorkshire and Humber Excel spreadsheets were missing header rows. These have been manually inserted before processing to ensure data consistency across all regions.

## Features

### Interactive Dashboard

- **Two-Tab Interface**:
  - **England by region**: Aggregate regional analysis with toggle between all England or filtered regions
  - **In your area**: Organisation-level analysis filtered by regime type (PCT, CCG, ICB) and region

- **Rich Visualizations**:
  - Stacked bar charts showing female/male admission trends over time
  - Injury type analysis with both count and percentage breakdowns
  - Regional and organisational comparison charts
  - Gender distribution pie charts and grouped bar charts
  - Interactive Plotly charts with hover details

- **Advanced Filtering**:
  - Year range selection with slider
  - Multi-select region filtering
  - Regime type filtering (PCT, CCG, ICB)
  - Region-based organisation filtering
  - Multi-organisation comparison support

- **Data Analysis Features**:
  - Key metrics display (total admissions, average rates, gender breakdown)
  - Conditional analysis sections (only show when multiple regions/organisations selected)
  - Text wrapping for long organisation names in charts
  - Downloadable filtered datasets as CSV

- **Injury Type Coverage**:
  - Head injuries
  - Stroke
  - Meningitis
  - Brain tumours
  - Other disorders
  - Abscess
  - Anoxia
  - CO poisoning

### Data Processing Pipeline

- **Automated Excel Processing**: Handles complex multi-sheet workbooks
- **Intelligent Header Detection**: Automatically standardizes scattered headers
- **Metadata Enrichment**: Adds regime type, financial year, and organisation columns
- **Multi-stage Transformation**: Three-stage pipeline for robust data cleaning

## Installation

1. Clone the repository or download the project files

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure the Excel files are in the `england_data/` directory

## Usage

### Running the Dashboard

To launch the interactive dashboard:

```bash
streamlit run dashboard.py
```

The dashboard will open in your web browser at `http://localhost:8501`.

### Dashboard Navigation

#### England by Region Tab

**Filters (Sidebar)**:
- **View Mode**: Toggle between "England" (all regions) or "By Regions" (filtered)
- **Select Regions**: Multi-select regions (only shown when "By Regions" is selected)
- **Select Year Range**: Slider to filter by financial year range

**Visualizations**:
- Key metrics overview
- Trends over time (stacked bar chart: Female/Male)
- Regional analysis (shown when multiple regions selected):
  - Total admissions by region
  - Average admission rate by region
- Injury type analysis over time:
  - Count stacked bar chart
  - Percentage stacked bar chart
- Gender/sex analysis:
  - Distribution pie chart
  - Top injury types by sex
- Detailed data table with download

#### In Your Area Tab

**Filters (Sidebar)**:
- **Select Regime Type**: Choose PCT, CCG, or ICB
- **Select Region**: Filter organisations by region (or "All")
- **Select Organisation(s)**: Multi-select organisations within the chosen regime and region
- **Select Year Range**: Slider to filter by available years

**Visualizations**:
- Organisation information header
- Key metrics overview
- Trends over time (stacked bar chart)
- Organisation comparison (shown when multiple organisations selected):
  - Total admissions by organisation
  - Average admission rate by organisation
- Injury type analysis over time (count and percentage)
- Gender/sex analysis
- Detailed data table with download

## Data Processing Pipeline

The project includes a three-stage automated data processing pipeline that transforms raw Excel files into analysis-ready CSV files:

### Stage 1: Excel Processing (`excel_processor.py`)

Extracts and transforms data from Excel files:
- Reads all Excel files from `england_data/` folder
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
- Regional total files (`Regional_total.csv`)
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
├── East/
│   ├── East.csv                  # Regional combined file
│   ├── Regional_total.csv        # Regional totals
│   ├── 2006_07.csv               # Individual year files
│   ├── 2007_08.csv
│   └── ...
├── East_Midlands/
│   ├── East_Midlands.csv
│   ├── Regional_total.csv
│   └── ...
├── London/
│   ├── London.csv
│   ├── Regional_total.csv
│   └── ...
├── North_East/
│   └── ...
├── North_West/
│   └── ...
├── South_East/
│   └── ...
├── South_West/
│   └── ...
├── West_Midlands/
│   └── ...
└── Yorkshire_and_Humberside/
    └── ...
```

## File Structure

```
├── england_data/                 # Source Excel files
│   ├── london-residents-abi-admissions.xlsx
│   ├── south-west-residents-abi-admissions.xlsx
│   ├── east-midlands-residents-abi-admissions.xlsx
│   └── ... (all 9 regional Excel files)
├── processed_data/               # Processed CSV files (generated)
│   ├── England.csv              # Master combined file
│   └── [Region]/                # Region-specific subfolders
│       ├── [Region].csv         # Regional combined file
│       ├── Regional_total.csv   # Regional totals
│       └── [Year].csv           # Individual year files
├── excel_processor.py           # Stage 1: Excel extraction and transformation
├── csv_processor.py             # Stage 2: CSV header standardization
├── csv_combiner.py              # Stage 3: Data combination
├── dashboard.py                 # Main Streamlit dashboard
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Technical Details

- **Framework**: Streamlit for the web interface
- **Visualization**: Plotly for interactive charts (with text wrapping support)
- **Data Processing**: Pandas for data manipulation
- **Excel Handling**: openpyxl for Excel file processing
- **Data Caching**: Streamlit's `@st.cache_data` decorator for performance

### Key Technical Features

- **Responsive Design**: Charts adapt to container width
- **Dynamic Filtering**: Filters update based on data availability
- **Conditional Rendering**: Analysis sections only shown when relevant
- **Text Wrapping**: Long organisation names automatically wrap across multiple lines
- **Data Type Handling**: Automatic conversion of numeric columns with error coercion
- **Year Extraction**: Financial years parsed to extract start year for sorting

## Data Structure

### Columns in Processed Data

**Metadata**:
- `Region`: England region name
- `Organisation`: Healthcare organisation name
- `FinancialYear`: Financial year (e.g., "2006-07")
- `Regime`: Organisation type (PCT, CCG, or ICB)
- `Year_Start`: Extracted start year for sorting (e.g., 2006)

**Injury Types** (each with Female_Count, Male_Count, Total_Count, Female_Rate, Male_Rate, Total_Rate):
- All_ABI (All acquired brain injuries)
- Head_injuries
- Stroke
- Meningitis
- Brain_tumour
- Other_disorders
- Abscess
- Anoxia
- CO_poisoning (Carbon monoxide poisoning)

## Notes

- The Excel files contain data in non-standard formats with headers scattered throughout
- The processor automatically handles these formatting challenges
- Data is cached for improved performance on subsequent loads
- All visualizations are interactive and responsive
- Regime types are determined by year:
  - 2006-2012: PCT (Primary Care Trust)
  - 2013-2021: CCG (Clinical Commissioning Group)
  - 2022+: ICB (Integrated Care Board)

## Troubleshooting

If you encounter issues:

1. **Missing Data File**: Ensure `processed_data/England.csv` exists
   - If not, run the data processing pipeline (excel_processor.py → csv_processor.py → csv_combiner.py)

2. **Excel Files Not Found**: Check that all 9 regional Excel files are in the `england_data/` folder

3. **Dependencies Issues**: Reinstall dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. **Deprecation Warnings**: Ensure you're using a stable Streamlit version
   ```bash
   pip install streamlit==1.28.0
   ```

5. **Data Type Errors**: The pipeline automatically handles data type conversion, but ensure Excel files are not corrupted

6. **Port Already in Use**: If port 8501 is busy, specify a different port:
   ```bash
   streamlit run dashboard.py --server.port 8502
   ```

## Contributing

This dashboard is designed to be easily extensible. You can:
- Add new visualization types to the dashboard tabs
- Modify the data processing logic for different Excel formats
- Add new metrics or filtering options
- Customize the color schemes and styling
- Add additional analysis sections (e.g., age groups, ethnicity if available)
- Extend to include UK-wide data (Scotland, Wales, Northern Ireland)

## Future Enhancements

Potential improvements:
- [ ] Add geographical mapping with NUTS1 boundaries
- [ ] Include predictive analytics and trend forecasting
- [ ] Add year-over-year comparison features
- [ ] Implement custom date range selection
- [ ] Add export to PDF/PowerPoint functionality
- [ ] Include statistical significance testing
- [ ] Add data quality indicators and completeness metrics

## License

This project is designed for analysis of public health data. Please ensure appropriate data handling and privacy considerations when deploying or sharing.

## Data Source

**Data Source**: NHS England ABI Admissions Data (Regional Statistics)  
**Dashboard created with**: Streamlit & Plotly  
**Processing Pipeline**: Python with Pandas, openpyxl
