"""
Streamlit Dashboard for England ABI (Acquired Brain Injury) Admissions Data
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="ABI Admissions in England - Data Dashboard",
    page_icon="🏥",
    layout="wide"
)

@st.cache_data
def load_data(cache_key=None):
    """Load and prepare the England ABI admissions data."""
    import os
    file_path = 'processed_data/England.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        st.error("Data file not found. Please run the data processing pipeline first.")
        st.stop()
    
    # Clean column names - handle the space in "Meningitis_Total _Rate"
    df.columns = df.columns.str.strip()
     
    # Convert numeric columns to proper numeric types
    numeric_cols = [col for col in df.columns if 'Count' in col or 'Rate' in col]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Extract year from FinancialYear for easier sorting
    df['Year_Start'] = df['FinancialYear'].str.split('-').str[0].astype(int)
    
    return df

# Load data with cache key based on file modification time
import os
cache_key = os.path.getmtime('processed_data/England.csv') if os.path.exists('processed_data/England.csv') else 0
df = load_data(cache_key)

# Title and introduction
st.title("🏥 Acquired Brain Injury (ABI) Hospital Admissions in England")

# Create tabs
tab1, tab2 = st.tabs(["📊 England by region", "📍 In your area"])

# ============================================================================
# TAB 1: ENGLAND OVERVIEW
# ============================================================================
with tab1:
    # Sidebar filters for England tab
    st.sidebar.header("England by region: filters")
    
    # View toggle
    view_mode = st.sidebar.radio(
        "View Mode",
        options=["England", "By Regions"],
        key="view_mode",
        help="Choose between viewing all of England or filtering by specific regions"
    )
    
    # Year range filter
    years = sorted(df['Year_Start'].unique())
    year_range = st.sidebar.select_slider(
        "Select Year Range",
        options=years,
        value=(min(years), max(years)),
        key="england_years"
    )
    
    # Region filter - only show if "By Regions" is selected
    all_regions = sorted(df['Region'].unique())
    if view_mode == "By Regions":
        selected_regions = st.sidebar.multiselect(
            "Select Regions",
            options=all_regions,
            default=all_regions[:3] if len(all_regions) >= 3 else all_regions,
            key="england_regions",
            help="Select one or more regions to analyze"
        )
    else:
        # If "England" mode, use all regions
        selected_regions = all_regions
    
    # Filter data
    filtered_df = df[
        (df['Year_Start'] >= year_range[0]) &
        (df['Year_Start'] <= year_range[1]) &
        (df['Region'].isin(selected_regions))
    ]
    
     
    # Show selection info based on view mode
    if view_mode == "England":
        st.markdown(f"**Viewing:** All of England")
    else:
        # Create a formatted list of regions
        if len(selected_regions) == len(all_regions):
            regions_text = "All Regions"
        elif len(selected_regions) <= 3:
            regions_text = ", ".join(selected_regions)
        else:
            regions_text = f"{len(selected_regions)} Regions Selected"
        st.markdown(f"**Regions:** {regions_text}")
    
    st.markdown(f"**Time Period:** {year_range[0]}-{year_range[0]+1} to {year_range[1]}-{year_range[1]+1}")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_admissions = filtered_df['All_ABI__Total_Count'].sum()
        st.metric("Total ABI Admissions", f"{total_admissions:,.0f}")
    
    with col2:
        avg_rate = filtered_df['All_ABI__Total_Rate'].mean()
        st.metric("Average Admission Rate", f"{avg_rate:.1f}")
    
    with col3:
        female_total = filtered_df['All_ABI__Female_Count'].sum()
        st.metric("Female Admissions", f"{female_total:,.0f}")
    
    with col4:
        male_total = filtered_df['All_ABI__Male_Count'].sum()
        st.metric("Male Admissions", f"{male_total:,.0f}")

    # Aggregate by year
    yearly_data = filtered_df.groupby('FinancialYear').agg({
        'All_ABI__Total_Count': 'sum',
        'All_ABI__Female_Count': 'sum',
        'All_ABI__Male_Count': 'sum',
        'Year_Start': 'first'
    }).reset_index().sort_values('Year_Start')
    
    
    
    # Create stacked bar chart using the working configuration
    fig_trends = go.Figure()
    fig_trends.add_trace(go.Bar(
        x=yearly_data['FinancialYear'], 
        y=yearly_data['All_ABI__Female_Count'],
        name='Female',
        marker_color='#FF6B9D',
        customdata=list(zip(yearly_data['All_ABI__Male_Count'], yearly_data['All_ABI__Total_Count'])),
    ))
    fig_trends.add_trace(go.Bar(
        x=yearly_data['FinancialYear'], 
        y=yearly_data['All_ABI__Male_Count'],
        name='Male',
        marker_color='#4D96FF',
        customdata=list(zip(yearly_data['All_ABI__Female_Count'], yearly_data['All_ABI__Total_Count'])),
    ))
    
    fig_trends.update_layout(
        title="ABI Admissions Over Time",
        xaxis_title="Financial Year",
        yaxis_title="Number of Admissions",
        barmode='stack',
        hovermode='x unified',
        height=500,
        xaxis={
            'type': 'category', 
            'categoryorder': 'array', 
            'categoryarray': yearly_data['FinancialYear'].tolist()
        }
    )
    
    st.plotly_chart(fig_trends, use_container_width=True)

    # Regional comparison - only show if more than one region is selected
    if len(selected_regions) > 1:
        st.header("🗺️ Regional Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Total admissions by region
            regional_totals = filtered_df.groupby('Region')['All_ABI__Total_Count'].sum().sort_values(ascending=True)
            
            fig_regional = px.bar(
                x=regional_totals.values,
                y=regional_totals.index,
                orientation='h',
                title="Total Admissions by Region",
                labels={'x': 'Total Admissions', 'y': 'Region'}
            )
            fig_regional.update_layout(height=400)
            st.plotly_chart(fig_regional, use_container_width=True)
        
        with col2:
            # Average admission rate by region
            regional_rates = filtered_df.groupby('Region')['All_ABI__Total_Rate'].mean().sort_values(ascending=True)
            
            fig_rates = px.bar(
                x=regional_rates.values,
                y=regional_rates.index,
                orientation='h',
                title="Average Admission Rate by Region",
                labels={'x': 'Average Rate', 'y': 'Region'},
                color=regional_rates.values,
                color_continuous_scale='Viridis'
            )
            fig_rates.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_rates, use_container_width=True)

    # Injury type breakdown over time
    st.header("🧠 Injury Type Analysis Over Time")
    
    # Aggregate injury types by year
    injury_types = {
        'Head Injuries': 'Head_injuries_Total_Count',
        'Stroke': 'Stroke_Total_Count',
        'Meningitis': 'Meningitis_Total_Count',
        'Brain Tumour': 'Brain_tumour_Total_Count',
        'Other Disorders': 'Other_disorders_Total_Count',
        'Abscess': 'Abscess_Total_Count',
        'Anoxia': 'Anoxia_Total_Count',
        'CO Poisoning': 'CO_poisoning_Total_Count'
    }
    
    # Create data for each year and injury type
    yearly_injury_data = []
    for year in sorted(filtered_df['FinancialYear'].unique()):
        year_df = filtered_df[filtered_df['FinancialYear'] == year]
        year_total = year_df['All_ABI__Total_Count'].sum()
        
        for injury_name, col_name in injury_types.items():
            injury_count = year_df[col_name].sum()
            injury_pct = (injury_count / year_total * 100) if year_total > 0 else 0
            yearly_injury_data.append({
                'FinancialYear': year,
                'Injury Type': injury_name,
                'Count': injury_count,
                'Percentage': injury_pct
            })
    
    injury_time_df = pd.DataFrame(yearly_injury_data)
    
    # Stacked bar chart (counts)
    fig_injury_count = px.bar(
        injury_time_df,
        x='FinancialYear',
        y='Count',
        color='Injury Type',
        title='Injury Type Admissions Over Time (Count)',
        labels={'Count': 'Number of Admissions'},
        hover_data={'Count': ':,.0f'}
    )
    
    fig_injury_count.update_layout(
        barmode='stack',
        xaxis={
            'tickangle': -45,
            'type': 'category', 
            'categoryorder': 'array', 
            'categoryarray': sorted(filtered_df['FinancialYear'].unique())
        },
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    st.plotly_chart(fig_injury_count, use_container_width=True)
    
    # Stacked percentage bar chart
    fig_injury_pct = px.bar(
        injury_time_df,
        x='FinancialYear',
        y='Percentage',
        color='Injury Type',
        title='Injury Type Distribution Over Time (Percentage)',
        labels={'Percentage': 'Percentage of Total Admissions (%)', 'FinancialYear': 'Financial Year'},
        hover_data={'Count': ':,.0f', 'Percentage': ':.1f'}
    )
    
    fig_injury_pct.update_layout(
        barmode='stack',
        xaxis={
            'tickangle': -45,
            'type': 'category', 
            'categoryorder': 'array', 
            'categoryarray': sorted(filtered_df['FinancialYear'].unique())
        },
        yaxis={'range': [0, 100]},
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    st.plotly_chart(fig_injury_pct, use_container_width=True)

    # Sex comparison
    st.header("👥 Sex Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sex distribution pie chart
        gender_data = pd.DataFrame({
            'Sex': ['Female', 'Male'],
            'Count': [filtered_df['All_ABI__Female_Count'].sum(), 
                     filtered_df['All_ABI__Male_Count'].sum()]
        })
        
        fig_gender = px.pie(
            gender_data,
            values='Count',
            names='Sex',
            title="Sex Distribution of ABI Admissions",
            color_discrete_sequence=['#FF6B9D', '#4D96FF']
        )
        st.plotly_chart(fig_gender, use_container_width=True)
    
    with col2:
        # Sex comparison by injury type
        gender_by_type = []
        for name, col_base in [('Head Injuries', 'Head_injuries'), ('Stroke', 'Stroke'), 
                               ('Meningitis', 'Meningitis'), ('Brain Tumour', 'Brain_tumour')]:
            gender_by_type.append({
                'Injury Type': name,
                'Female': filtered_df[f'{col_base}_Female_Count'].sum(),
                'Male': filtered_df[f'{col_base}_Male_Count'].sum()
            })
        
        gender_type_df = pd.DataFrame(gender_by_type)
        gender_type_df_melted = gender_type_df.melt(
            id_vars=['Injury Type'], 
            var_name='Sex', 
            value_name='Count'
        )
        
        fig_gender_type = px.bar(
            gender_type_df_melted,
            x='Injury Type',
            y='Count',
            color='Sex',
            barmode='group',
            title="Top Injury Types by Sex",
            color_discrete_sequence=['#FF6B9D', '#4D96FF']
        )
        st.plotly_chart(fig_gender_type, use_container_width=True)

    # Detailed data table
    st.header("📋 Detailed Data")
    
    # Allow users to select which columns to view
    view_option = st.radio(
        "Select view:",
        ["Summary", "All Columns"],
        key="england_view"
    )
    
    if view_option == "Summary":
        display_cols = ['Region', 'FinancialYear', 'Organisation', 
                       'All_ABI__Total_Count', 'All_ABI__Total_Rate',
                       'All_ABI__Female_Count', 'All_ABI__Male_Count']
        # Sort the full dataframe first, then select columns
        sorted_df = filtered_df.sort_values(['Region', 'Year_Start'])
        st.dataframe(
            sorted_df[display_cols],
            use_container_width=True,
            height=400
        )
    else:
        st.dataframe(
            filtered_df.sort_values(['Region', 'Year_Start']),
            use_container_width=True,
            height=400
        )
    
    # Download filtered data
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='filtered_abi_admissions.csv',
        mime='text/csv',
        key="england_download"
    )

# ============================================================================
# TAB 2: In your area (ORGANISATION LEVEL)
# ============================================================================
with tab2:
    st.sidebar.header("In your area: filters")
    
    # Get available regimes (filter out NaN values)
    all_regimes = sorted(df['Regime'].dropna().unique())
    
    # Regime selector
    selected_regime = st.sidebar.selectbox(
        "Select Regime Type",
        options=all_regimes,
        key="regime_selector",
        help="Filter organisations by regime type (e.g., PCT, CCG, ICB)"
    )
    
    # Region selector
    all_org_regions = ["All"] + sorted(df['Region'].dropna().unique())
    selected_org_region = st.sidebar.selectbox(
        "Select Region",
        options=all_org_regions,
        key="org_region_selector",
        help="Filter organisations by region"
    )
    
    # Filter organisations by regime and region
    if selected_org_region == "All":
        regime_orgs = sorted(df[df['Regime'] == selected_regime]['Organisation'].dropna().unique())
    else:
        regime_orgs = sorted(df[(df['Regime'] == selected_regime) & 
                                (df['Region'] == selected_org_region)]['Organisation'].dropna().unique())
    
    # Organisation multi-selector
    if selected_org_region == "All":
        org_help_text = f"Select one or more organisations from {selected_regime}"
    else:
        org_help_text = f"Select one or more organisations from {selected_regime} in {selected_org_region}"
    
    selected_orgs = st.sidebar.multiselect(
        "Select Organisation(s)",
        options=regime_orgs,
        default=regime_orgs[:1] if regime_orgs else [],
        key="org_selector",
        help=org_help_text
    )
    
    if not selected_orgs:
        st.warning("⚠️ Please select at least one organisation to display data.")
        st.stop()
    
    # Filter data for selected organisations
    org_df = df[df['Organisation'].isin(selected_orgs)].copy()
    
    # Get available years for selected organisations
    org_years = sorted(org_df['Year_Start'].unique())
    
    if len(org_years) > 1:
        org_year_range = st.sidebar.select_slider(
            "Select Year Range",
            options=org_years,
            value=(min(org_years), max(org_years)),
            key="org_years"
        )
        org_filtered_df = org_df[
            (org_df['Year_Start'] >= org_year_range[0]) &
            (org_df['Year_Start'] <= org_year_range[1])
        ]
    else:
        org_filtered_df = org_df
        st.sidebar.info(f"Only {len(org_years)} year(s) available for selected organisation(s)")
    
    # Get regions for selected orgs
    org_regions = org_filtered_df['Region'].unique()
    
    # Organisation info header
    if len(selected_orgs) == 1:
        st.header(f"📍 {selected_orgs[0]}")
        org_region = org_filtered_df['Region'].iloc[0] if len(org_filtered_df) > 0 else "Unknown"
        st.markdown(f"**Regime:** {selected_regime}")
        st.markdown(f"**Region:** {org_region}")
        st.markdown(f"**Data available:** {min(org_years)} - {max(org_years)}")
    else:
        st.header(f"📍 {len(selected_orgs)} Organisations ({selected_regime})")
        st.markdown(f"**Regions:** {', '.join(sorted(org_regions))}")
        st.markdown(f"**Data available:** {min(org_years)} - {max(org_years)}")
        
        # List of organisations
        if len(selected_orgs) <= 10:
            # Show full list if 10 or fewer
            st.markdown(f"**Organisations:** {', '.join(selected_orgs)}")
        else:
            # Show expandable list if more than 10
            with st.expander(f"View all {len(selected_orgs)} organisations"):
                for i, org in enumerate(selected_orgs, 1):
                    st.write(f"{i}. {org}")
    
    # Key metrics for organisation
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        org_total = org_filtered_df['All_ABI__Total_Count'].sum()
        st.metric("Total ABI Admissions", f"{org_total:,.0f}")
    
    with col2:
        org_avg_rate = org_filtered_df['All_ABI__Total_Rate'].mean()
        st.metric("Average Admission Rate", f"{org_avg_rate:.1f}")
    
    with col3:
        org_female_total = org_filtered_df['All_ABI__Female_Count'].sum()
        st.metric("Female Admissions", f"{org_female_total:,.0f}")
    
    with col4:
        org_male_total = org_filtered_df['All_ABI__Male_Count'].sum()
        st.metric("Male Admissions", f"{org_male_total:,.0f}")
    
    # Trends over time for organisation(s)
    st.subheader("📈 Trends Over Time")
    
    org_yearly_data = org_filtered_df.groupby('FinancialYear').agg({
        'All_ABI__Total_Count': 'sum',
        'All_ABI__Female_Count': 'sum',
        'All_ABI__Male_Count': 'sum',
        'Year_Start': 'first'
    }).reset_index().sort_values('Year_Start')
    
    # Create stacked bar chart
    fig_org_trends = go.Figure()
    fig_org_trends.add_trace(go.Bar(
        x=org_yearly_data['FinancialYear'], 
        y=org_yearly_data['All_ABI__Female_Count'],
        name='Female',
        marker_color='#FF6B9D'
    ))
    fig_org_trends.add_trace(go.Bar(
        x=org_yearly_data['FinancialYear'], 
        y=org_yearly_data['All_ABI__Male_Count'],
        name='Male',
        marker_color='#4D96FF'
    ))
    
    # Dynamic title based on selection
    org_title = selected_orgs[0] if len(selected_orgs) == 1 else f"{len(selected_orgs)} {selected_regime} Organisations"
    
    fig_org_trends.update_layout(
        title=f"ABI Admissions Over Time - {org_title}",
        xaxis_title="Financial Year",
        yaxis_title="Number of Admissions",
        barmode='stack',
        hovermode='x unified',
        height=400,
        xaxis={'tickangle': -45}
    )
    st.plotly_chart(fig_org_trends, use_container_width=True)
    
    # Organisation comparison - only show if more than one organisation is selected
    if len(selected_orgs) > 1:
        st.subheader("🏥 Organisation Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Total admissions by organisation
            org_totals = org_filtered_df.groupby('Organisation')['All_ABI__Total_Count'].sum().sort_values(ascending=True)
            
            # Wrap long organisation names
            wrapped_names = []
            for name in org_totals.index:
                if len(name) > 40:
                    # Split into chunks of ~40 characters at word boundaries
                    words = name.split()
                    lines = []
                    current_line = []
                    current_length = 0
                    for word in words:
                        if current_length + len(word) + 1 > 40 and current_line:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                            current_length = len(word)
                        else:
                            current_line.append(word)
                            current_length += len(word) + 1
                    if current_line:
                        lines.append(' '.join(current_line))
                    wrapped_names.append('<br>'.join(lines))
                else:
                    wrapped_names.append(name)
            
            fig_org_totals = px.bar(
                x=org_totals.values,
                y=wrapped_names,
                orientation='h',
                title="Total Admissions by Organisation",
                labels={'x': 'Total Admissions', 'y': 'Organisation'}
            )
            fig_org_totals.update_layout(
                height=max(400, len(org_totals) * 35),
                yaxis={'automargin': True},
                margin=dict(l=200)
            )
            st.plotly_chart(fig_org_totals, use_container_width=True)
        
        with col2:
            # Average admission rate by organisation
            org_rates = org_filtered_df.groupby('Organisation')['All_ABI__Total_Rate'].mean().sort_values(ascending=True)
            
            # Wrap long organisation names (same logic)
            wrapped_names_rates = []
            for name in org_rates.index:
                if len(name) > 40:
                    words = name.split()
                    lines = []
                    current_line = []
                    current_length = 0
                    for word in words:
                        if current_length + len(word) + 1 > 40 and current_line:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                            current_length = len(word)
                        else:
                            current_line.append(word)
                            current_length += len(word) + 1
                    if current_line:
                        lines.append(' '.join(current_line))
                    wrapped_names_rates.append('<br>'.join(lines))
                else:
                    wrapped_names_rates.append(name)
            
            fig_org_rates = px.bar(
                x=org_rates.values,
                y=wrapped_names_rates,
                orientation='h',
                title="Average Admission Rate by Organisation",
                labels={'x': 'Average Rate', 'y': 'Organisation'},
                color=org_rates.values,
                color_continuous_scale='Viridis'
            )
            fig_org_rates.update_layout(
                height=max(400, len(org_rates) * 35),
                yaxis={'automargin': True},
                margin=dict(l=200),
                showlegend=False
            )
            st.plotly_chart(fig_org_rates, use_container_width=True)
    
    # Injury type breakdown over time for organisation
    st.subheader("🧠 Injury Type Analysis Over Time")
    
    org_injury_types = {
        'Head Injuries': 'Head_injuries_Total_Count',
        'Stroke': 'Stroke_Total_Count',
        'Meningitis': 'Meningitis_Total_Count',
        'Brain Tumour': 'Brain_tumour_Total_Count',
        'Other Disorders': 'Other_disorders_Total_Count',
        'Abscess': 'Abscess_Total_Count',
        'Anoxia': 'Anoxia_Total_Count',
        'CO Poisoning': 'CO_poisoning_Total_Count'
    }
    
    # Create data for each year and injury type
    org_yearly_injury_data = []
    for year in sorted(org_filtered_df['FinancialYear'].unique()):
        year_df = org_filtered_df[org_filtered_df['FinancialYear'] == year]
        year_total = year_df['All_ABI__Total_Count'].sum()
        
        for injury_name, col_name in org_injury_types.items():
            injury_count = year_df[col_name].sum()
            injury_pct = (injury_count / year_total * 100) if year_total > 0 else 0
            org_yearly_injury_data.append({
                'FinancialYear': year,
                'Injury Type': injury_name,
                'Count': injury_count,
                'Percentage': injury_pct
            })
    
    org_injury_time_df = pd.DataFrame(org_yearly_injury_data)
    
    # Stacked bar chart (counts)
    fig_org_injury_count = px.bar(
        org_injury_time_df,
        x='FinancialYear',
        y='Count',
        color='Injury Type',
        title=f'Injury Type Admissions Over Time - {org_title} (Count)',
        labels={'Count': 'Number of Admissions'},
        hover_data={'Count': ':,.0f'}
    )
    
    fig_org_injury_count.update_layout(
        barmode='stack',
        xaxis={'tickangle': -45},
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    st.plotly_chart(fig_org_injury_count, use_container_width=True)
    
    # Stacked percentage bar chart
    fig_org_injury_pct = px.bar(
        org_injury_time_df,
        x='FinancialYear',
        y='Percentage',
        color='Injury Type',
        title=f'Injury Type Distribution Over Time - {org_title} (Percentage)',
        labels={'Percentage': 'Percentage of Total Admissions (%)', 'FinancialYear': 'Financial Year'},
        hover_data={'Count': ':,.0f', 'Percentage': ':.1f'}
    )
    
    fig_org_injury_pct.update_layout(
        barmode='stack',
        xaxis={'tickangle': -45},
        yaxis={'range': [0, 100]},
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    st.plotly_chart(fig_org_injury_pct, use_container_width=True)
    
    # Sex analysis for organisation
    st.subheader("👥 Sex Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        org_gender_data = pd.DataFrame({
            'Sex': ['Female', 'Male'],
            'Count': [org_filtered_df['All_ABI__Female_Count'].sum(), 
                     org_filtered_df['All_ABI__Male_Count'].sum()]
        })
        
        fig_org_gender = px.pie(
            org_gender_data,
            values='Count',
            names='Sex',
            title=f"Sex Distribution - {org_title}",
            color_discrete_sequence=['#FF6B9D', '#4D96FF']
        )
        st.plotly_chart(fig_org_gender, use_container_width=True)
    
    with col2:
        # Sex comparison by injury type for org
        org_gender_by_type = []
        for name, col_base in [('Head Injuries', 'Head_injuries'), ('Stroke', 'Stroke'), 
                               ('Meningitis', 'Meningitis'), ('Brain Tumour', 'Brain_tumour')]:
            female_count = org_filtered_df[f'{col_base}_Female_Count'].sum()
            male_count = org_filtered_df[f'{col_base}_Male_Count'].sum()
            if female_count + male_count > 0:
                org_gender_by_type.append({
                    'Injury Type': name,
                    'Female': female_count,
                    'Male': male_count
                })
        
        if org_gender_by_type:
            org_gender_type_df = pd.DataFrame(org_gender_by_type)
            org_gender_type_df_melted = org_gender_type_df.melt(
                id_vars=['Injury Type'], 
                var_name='Sex', 
                value_name='Count'
            )
            
            fig_org_gender_type = px.bar(
                org_gender_type_df_melted,
                x='Injury Type',
                y='Count',
                color='Sex',
                barmode='group',
                title=f"Top Injury Types by Sex - {org_title}",
                color_discrete_sequence=['#FF6B9D', '#4D96FF']
            )
            st.plotly_chart(fig_org_gender_type, use_container_width=True)
    
    # Detailed data table for organisation
    st.subheader("📋 Detailed Data")
    
    view_option_org = st.radio(
        "Select view:",
        ["Summary", "All Columns"],
        key="org_view"
    )
    
    if view_option_org == "Summary":
        display_cols_org = ['Region', 'FinancialYear', 'Organisation', 
                           'All_ABI__Total_Count', 'All_ABI__Total_Rate',
                           'All_ABI__Female_Count', 'All_ABI__Male_Count']
        sorted_org_df = org_filtered_df.sort_values(['Year_Start'])
        st.dataframe(
            sorted_org_df[display_cols_org],
            use_container_width=True,
            height=400
        )
    else:
        st.dataframe(
            org_filtered_df.sort_values(['Year_Start']),
            use_container_width=True,
            height=400
        )
    
    # Download filtered data
    # Create filename based on selection
    if len(selected_orgs) == 1:
        filename = f'{selected_orgs[0].replace(" ", "_")}_abi_admissions.csv'
    else:
        filename = f'{selected_regime.replace(" ", "_")}_organisations_abi_admissions.csv'
    
    st.download_button(
        label="📥 Download Organisation Data as CSV",
        data=org_filtered_df.to_csv(index=False).encode('utf-8'),
        file_name=filename,
        mime='text/csv',
        key="org_download"
    )

# Footer
st.markdown("---")
st.markdown("""
**Data Source:** England ABI Admissions Data  
**Dashboard created with:** Streamlit & Plotly
""")

