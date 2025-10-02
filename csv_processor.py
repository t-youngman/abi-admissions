"""
CSV Data Processor for ABI Admissions Data

This script processes all CSV files in the processed_data folder according to
specific requirements:
1. Replace spaces with underscores in the first row
2. Concatenate first and second row contents for each column (excluding first column)
2.5. Copy contents of first cell in second row to a new column for all rows
3. Copy first cell contents to a new first column for all rows
4. Replace first cell contents with 'Financial_Year'
5. Delete the second row
6. Remove text after underscore in first two columns
7. Replace the cell at the first row of the third column with 'Organisation'
8. Standardize Financial Year formatting to YYYY-YY format
9. Process Total_Count rows (change to 'unknown' and zero numeric values)

Author: Computational Social Scientist
Date: 2025
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import glob
import re


def standardize_financial_year(year_string):
    """
    Standardize financial year formatting to YYYY-YY format.
    
    Args:
        year_string (str): Financial year string in various formats
        
    Returns:
        str: Standardized financial year in YYYY-YY format
    """
    if pd.isna(year_string) or not year_string:
        return year_string
    
    year_str = str(year_string).strip()
    
    # Pattern to match YYYY-YYYY format
    full_year_pattern = r'^(\d{4})-(\d{4})$'
    match = re.match(full_year_pattern, year_str)
    
    if match:
        start_year = int(match.group(1))
        end_year = int(match.group(2))
        
        # Convert to YYYY-YY format
        end_year_short = str(end_year)[-2:]
        return f"{start_year}-{end_year_short}"
    
    # If already in YYYY-YY format or other format, return as is
    return year_str


def process_total_count_rows(df):
    """
    Process rows where the organisation column equals 'Total_Count':
    1. Change 'Total_Count' to 'unknown' in the organisation column
    2. Set all numeric values between All_ABI__Female_Count and Other_disorders_Total_Rate to zero
    
    Args:
        df (pd.DataFrame): DataFrame to process (read with header=None)
        
    Returns:
        pd.DataFrame: Processed DataFrame with Total_Count rows modified
    """
    if df.empty:
        return df
    
    # Find the organisation column by looking at the first row (header row)
    org_column_idx = None
    for i in range(len(df.columns)):
        if str(df.iloc[0, i]).strip() == 'Organisation':
            org_column_idx = i
            break
    
    if org_column_idx is None:
        print("  [WARNING] Cannot process Total_Count rows - organisation column not found")
        return df
    
    # Find the start and end columns for numeric data
    start_col_idx = None
    end_col_idx = None
    
    for i in range(len(df.columns)):
        col_name = str(df.iloc[0, i]).strip()
        if col_name == 'All_ABI__Female_Count':
            start_col_idx = i
        elif col_name == 'Other_disorders_Total_Rate':
            end_col_idx = i
            break
    
    if start_col_idx is None or end_col_idx is None:
        print("  [WARNING] Cannot find numeric column range - skipping Total_Count processing")
        return df
    
    # Count rows to process
    total_count_rows = 0
    
    # Process rows where organisation = 'Total_Count'
    # Skip the header row (index 0) when processing
    for row_idx in range(1, len(df)):
        if str(df.iloc[row_idx, org_column_idx]).strip() == 'Total_Count':
            # Change 'Total_Count' to 'unknown'
            df.iloc[row_idx, org_column_idx] = 'unknown'
            
            # Set all numeric columns to zero
            for col_idx in range(start_col_idx, end_col_idx + 1):
                df.iloc[row_idx, col_idx] = 0
            
            total_count_rows += 1
    
    if total_count_rows > 0:
        print(f"  [PROCESS] Modified {total_count_rows} rows: 'Total_Count' -> 'unknown' and zeroed numeric values")
    
    return df


def process_csv_file(file_path):
    """
    Process a single CSV file according to the specified requirements.
    
    Args:
        file_path (str): Path to the CSV file to process
        
    Returns:
        pd.DataFrame: Processed dataframe
    """
    print(f"Processing: {file_path}")
    
    # Read the CSV file
    df = pd.read_csv(file_path, header=None)

    # Step 1: Replace spaces with underscores in the first row
    for col_idx in range(len(df.columns)):
        if pd.notna(df.iloc[0, col_idx]):
            original_value = str(df.iloc[0, col_idx])
            new_value = original_value.replace(' ', '_')
            df.iloc[0, col_idx] = new_value
            if original_value != new_value:
                print(f"  Replaced spaces with underscores: '{original_value}' -> '{new_value}'")
    
    # Step 2: Concatenate first and second row contents for each column (excluding first column)
    for col_idx in range(1, len(df.columns)):  # Start from column 1, skip first column
        first_cell = df.iloc[0, col_idx] if pd.notna(df.iloc[0, col_idx]) else ""
        second_cell = df.iloc[1, col_idx] if pd.notna(df.iloc[1, col_idx]) else ""
        
        if first_cell and second_cell:
            concatenated = f"{first_cell}_{second_cell}"
            df.iloc[0, col_idx] = concatenated
            print(f"  Concatenated column {col_idx}: '{first_cell}' + '{second_cell}' -> '{concatenated}'")
        elif first_cell:
            df.iloc[0, col_idx] = first_cell
        elif second_cell:
            df.iloc[0, col_idx] = second_cell
    
    # Step 2.5: Copy contents of first cell in second row to a new column for all rows
    second_row_first_cell = df.iloc[1, 0] if pd.notna(df.iloc[1, 0]) else ""
    
    # Remove all spaces from the value
    second_row_first_cell_cleaned = str(second_row_first_cell).replace(' ', '')
    
    # Insert a new column at the beginning
    df.insert(0, 'second_row_first_cell', second_row_first_cell_cleaned)
    
    # Fill all rows in the new first column with the cleaned second row first cell content
    for row_idx in range(len(df)):
        df.iloc[row_idx, 0] = second_row_first_cell_cleaned
    
    # Set the first row of this new column to 'Regime'
    df.iloc[0, 0] = 'Regime'
    
    print(f"  Added new first column with cleaned content: '{second_row_first_cell}' -> '{second_row_first_cell_cleaned}' (header: 'Regime')")
    
    # Step 3: Copy first row of second column contents to a new first column for all rows
    second_col_first_row_content = df.iloc[0, 1] if pd.notna(df.iloc[0, 1]) else ""
    
    # Insert a new column at the beginning
    df.insert(0, 'new_first_col', second_col_first_row_content)
    
    # Fill all rows in the new first column with the second column first row content
    for row_idx in range(1, len(df)):
        df.iloc[row_idx, 0] = second_col_first_row_content
    
    print(f"  Added new first column with second column first row content: '{second_col_first_row_content}'")
    
    # Step 4: Replace the contents of the first cell with 'Financial_Year'
    df.iloc[0, 0] = 'FinancialYear'
    print(f"  Replaced first cell with: 'FinancialYear'")
    
    # Step 5: Delete the second row
    df = df.drop(df.index[1]).reset_index(drop=True)
    print(f"  Deleted second row")
    
    # Step 6: Remove text after underscore in first two columns
    for col_idx in range(min(2, len(df.columns))):  # Only process first two columns
        for row_idx in range(len(df)):
            if pd.notna(df.iloc[row_idx, col_idx]):
                original_value = str(df.iloc[row_idx, col_idx])
                if '_' in original_value:
                    new_value = original_value.split('_')[0]
                    df.iloc[row_idx, col_idx] = new_value
                    print(f"  Removed text after underscore in column {col_idx}, row {row_idx}: '{original_value}' -> '{new_value}'")
    
    # Step 7: Replace the cell at the first row of the third column with 'Organisation'
    if len(df.columns) >= 3:
        original_value = df.iloc[0, 2] if pd.notna(df.iloc[0, 2]) else ""
        df.iloc[0, 2] = 'Organisation'
        print(f"  Replaced third column header '{original_value}' with 'Organisation'")
    
    # Step 8: Standardize Financial Year formatting to YYYY-YY format
    # Process the first column (Financial Year column) for all rows except header
    for row_idx in range(1, len(df)):
        if pd.notna(df.iloc[row_idx, 0]):
            original_value = str(df.iloc[row_idx, 0])
            standardized_value = standardize_financial_year(original_value)
            if original_value != standardized_value:
                df.iloc[row_idx, 0] = standardized_value
                print(f"  Standardized Financial Year: '{original_value}' -> '{standardized_value}'")
    
    # Step 9: Process Total_Count rows (change to 'unknown' and zero numeric values)
    df = process_total_count_rows(df)
    
    print(f"  Final shape: {df.shape}")
    return df


def process_all_csv_files(input_dir="processed_data"):
    """
    Process all CSV files in subfolders within the input directory.
    Each subfolder's CSV files are processed and saved back to the same subfolder.
    
    Args:
        input_dir (str): Base directory containing subfolders with CSV files
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist!")
        return
    
    # Find all subfolders
    subfolders = [f for f in input_path.iterdir() if f.is_dir()]
    
    if not subfolders:
        print(f"No subfolders found in '{input_dir}'")
        return
    
    print(f"Found {len(subfolders)} subfolders to process:")
    for folder in subfolders:
        print(f"  - {folder.name}")
    
    print("\n" + "="*60)
    print("PROCESSING CSV FILES IN SUBFOLDERS")
    print("="*60)
    
    processed_count = 0
    total_files_processed = 0
    
    for subfolder in subfolders:
        try:
            print(f"\n=== Processing subfolder: {subfolder.name} ===")
            
            # Find all CSV files in this subfolder
            csv_files = list(subfolder.glob("*.csv"))
            
            if not csv_files:
                print(f"  No CSV files found in {subfolder.name}, skipping...")
                continue
            
            print(f"  Found {len(csv_files)} CSV files")
            
            for csv_file in csv_files:
                try:
                    print(f"\n  --- Processing {csv_file.name} ---")
                    
                    # Process the CSV file
                    processed_df = process_csv_file(csv_file)
                    
                    # Save the processed file back to the same subfolder (overwrite)
                    output_file = subfolder / csv_file.name
                    processed_df.to_csv(output_file, index=False, header=False)
                    print(f"    Saved processed file: {output_file}")
                    
                    total_files_processed += 1
                    
                except Exception as e:
                    print(f"    Error processing {csv_file.name}: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            processed_count += 1
            
        except Exception as e:
            print(f"  Error processing subfolder {subfolder.name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n" + "="*60)
    print(f"PROCESSING COMPLETE")
    print(f"Successfully processed {processed_count} out of {len(subfolders)} subfolders")
    print(f"Total files processed: {total_files_processed}")
    print("="*60)


def main():
    """Main function to run the CSV processing."""
    print("CSV Data Processor for ABI Admissions Data")
    print("="*50)
    
    # Process all CSV files in the processed_data directory
    process_all_csv_files()


if __name__ == "__main__":
    main()
