"""
Excel Data Processor for ABI Admissions Data

This script processes the south-west-residents-abi-admissions Excel file according to
specific requirements:
1. Extract 'South West' tab and delete top 6 rows
2. Find and replace long 'Other disorders' text with 'Other'
3. Copy specific category values to 5 cells to the right
4. Concatenate 'Rate' with left cell content and underscore
5. Save as CSV

Author: Computational Social Scientist
Date: 2025
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import re


def examine_excel_structure(file_path):
    """Examine the structure of the Excel file to understand its format."""
    print(f"Examining Excel file: {file_path}")
    
    # Read all sheet names
    excel_file = pd.ExcelFile(file_path)
    print(f"Sheet names: {excel_file.sheet_names}")
    print(f"Number of sheets: {len(excel_file.sheet_names)}")
    
    # Read the second sheet (index 1) to examine structure
    if len(excel_file.sheet_names) >= 2:
        second_sheet_name = excel_file.sheet_names[1]
        print(f"\nExamining second sheet: '{second_sheet_name}'")
        df = pd.read_excel(file_path, sheet_name=second_sheet_name, header=None)
        print(f"Sheet shape: {df.shape}")
        print(f"First 10 rows and 10 columns:")
        print(df.iloc[:10, :10])
        
        # Look for the specific text to replace
        for idx, row in df.iterrows():
            for col_idx, cell in enumerate(row):
                if pd.notna(cell) and isinstance(cell, str):
                    if 'Other disorders (encephalitis' in cell:
                        print(f"\nFound 'Other disorders' text at row {idx}, col {col_idx}")
                        print(f"Full text: {cell}")
                        break
    else:
        print("File does not have at least 2 sheets!")
    
    return excel_file.sheet_names


def split_by_blank_rows(df):
    """
    Split dataframe by blank rows and return dictionary of dataframes.
    Each dataframe is named after the content of the first cell in the top-left.
    """
    split_dfs = {}
    current_table = []
    current_table_name = None
    
    for idx, row in df.iterrows():
        # Check if this is a blank row (all cells are NaN or empty)
        is_blank_row = True
        for cell in row:
            if pd.notna(cell) and str(cell).strip() != '':
                is_blank_row = False
                break
        
        if is_blank_row:
            # Save current table if it exists
            if current_table and current_table_name:
                table_df = pd.DataFrame(current_table)
                split_dfs[current_table_name] = table_df
                print(f"Found table: '{current_table_name}' with {len(current_table)} rows")
            
            # Reset for next table
            current_table = []
            current_table_name = None
        else:
            # Add row to current table
            current_table.append(row.tolist())
            
            # If this is the first row of a new table, get the table name
            if current_table_name is None:
                first_cell = row.iloc[0] if len(row) > 0 else None
                if pd.notna(first_cell) and str(first_cell).strip() != '':
                    current_table_name = str(first_cell).strip()
                else:
                    current_table_name = f"Table_{len(split_dfs) + 1}"
    
    # Don't forget the last table
    if current_table and current_table_name:
        table_df = pd.DataFrame(current_table)
        split_dfs[current_table_name] = table_df
        print(f"Found table: '{current_table_name}' with {len(current_table)} rows")
    
    return split_dfs


def process_abi_data(input_file, output_dir):
    """
    Process the ABI admissions Excel file according to specifications.
    
    Args:
        input_file (str): Path to input Excel file
        output_dir (Path): Base output directory (processed_data)
        
    Returns:
        tuple: (processed_df, sheet_name) - Processed dataframe and the sheet name used
    """
    print(f"Processing {input_file}...")
    
    # Get the second sheet (index 1) - different files have different sheet names
    excel_file = pd.ExcelFile(input_file)
    if len(excel_file.sheet_names) < 2:
        raise ValueError(f"File {input_file} does not have at least 2 sheets!")
    
    second_sheet_name = excel_file.sheet_names[1]
    print(f"Reading second sheet: '{second_sheet_name}'")
    
    # Clean the sheet name for use as a folder name
    clean_sheet_name = re.sub(r'[^\w\s-]', '', second_sheet_name).strip()
    clean_sheet_name = re.sub(r'[-\s]+', '_', clean_sheet_name)
    
    # Create output subfolder using the cleaned sheet name
    output_subfolder = output_dir / clean_sheet_name
    output_subfolder.mkdir(exist_ok=True)
    print(f"Created/verified directory: {output_subfolder}")
    
    # Read the second sheet, skipping the first 6 rows
    df = pd.read_excel(input_file, sheet_name=second_sheet_name, header=None, skiprows=6)
    print(f"Data shape after skipping 6 rows: {df.shape}")
    
    # Create a copy to work with
    processed_df = df.copy()
    
    # Step 1: Find and replace any cell beginning with 'Other disorders' with 'Other_disorders'
    for idx, row in processed_df.iterrows():
        for col_idx, cell in enumerate(row):
            if pd.notna(cell) and isinstance(cell, str):
                if cell.strip().startswith('Other disorders'):
                    processed_df.iloc[idx, col_idx] = 'Other_disorders'
                    print(f"Replaced '{cell[:50]}...' with 'Other_disorders' at ({idx}, {col_idx})")
    
    print("Replaced all cells beginning with 'Other disorders' with 'Other_disorders'")
    
    # Step 2: Copy specific category values to 5 cells to the right
    categories = ['All ABI', 'Head injuries', 'Stroke', 'Meningitis', 'Brain tumour', 
                  'Abscess', 'Anoxia', 'Other_disorders', 'CO poisoning']
    
    # Create a copy to track original values before any modifications
    original_df = processed_df.copy()
    
    for idx, row in original_df.iterrows():
        for col_idx, cell in enumerate(row):
            if pd.notna(cell) and str(cell).strip() in categories:
                # Only copy if the target cells are empty or contain different values
                # This prevents overwriting cells that have already been processed
                should_copy = True
                for i in range(1, 6):
                    if col_idx + i < len(row):
                        target_cell = processed_df.iloc[idx, col_idx + i]
                        if pd.notna(target_cell) and str(target_cell).strip() == str(cell).strip():
                            should_copy = False
                            break
                
                if should_copy:
                    # Copy to 5 cells to the right
                    for i in range(1, 6):
                        if col_idx + i < len(row):
                            processed_df.iloc[idx, col_idx + i] = cell
                    print(f"Copied '{cell}' from ({idx}, {col_idx}) to 5 cells to the right")
    
    # Step 3: Concatenate 'Rate' with left cell content and underscore
    for idx, row in processed_df.iterrows():
        for col_idx, cell in enumerate(row):
            if pd.notna(cell) and str(cell).strip() == 'Rate':
                # Get the cell to the left
                if col_idx > 0:
                    left_cell = processed_df.iloc[idx, col_idx - 1]
                    if pd.notna(left_cell):
                        new_value = f"{left_cell}_Rate"
                        processed_df.iloc[idx, col_idx] = new_value
                        print(f"Concatenated 'Rate' with '{left_cell}' to create '{new_value}'")
    
    # Step 4: Add '_Count' suffix to 'Female', 'Male', and 'Total' cells
    count_terms = ['Female', 'Male', 'Total']
    for idx, row in processed_df.iterrows():
        for col_idx, cell in enumerate(row):
            if pd.notna(cell):
                cell_str = str(cell).strip()
                # Check if cell contains any of the count terms (but not already processed)
                for term in count_terms:
                    if cell_str == term and not cell_str.endswith('_Count'):
                        new_value = f"{cell_str}_Count"
                        processed_df.iloc[idx, col_idx] = new_value
                        print(f"Added '_Count' suffix to '{cell_str}' to create '{new_value}'")
    
    # Step 5: Split data by blank rows and create separate CSV files
    split_dataframes = split_by_blank_rows(processed_df)
    
    # Save main processed file (using the cleaned sheet name as the filename)
    main_output_path = output_subfolder / f"{clean_sheet_name}.csv"
    processed_df.to_csv(main_output_path, index=False, header=False)
    print(f"Saved main processed data to {main_output_path}")
    
    # Save split files
    for i, (table_name, df) in enumerate(split_dataframes.items()):
        if df is not None and not df.empty:
            # Clean table name for filename
            clean_name = re.sub(r'[^\w\s-]', '', str(table_name)).strip()
            clean_name = re.sub(r'[-\s]+', '_', clean_name)
            if not clean_name:
                clean_name = f"table_{i+1}"
            
            split_output_path = output_subfolder / f"{clean_name}.csv"
            df.to_csv(split_output_path, index=False, header=False)
            print(f"Saved split data to {split_output_path} (from table: '{table_name}')")
    
    return processed_df, clean_sheet_name


def process_all_excel_files(input_dir="england_data", output_dir="processed_data"):
    """
    Process all Excel files in the input directory.
    
    Args:
        input_dir (str): Directory containing Excel files to process
        output_dir (str): Directory to save processed CSV files
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(exist_ok=True)
    
    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist!")
        return
    
    # Find all Excel files
    excel_files = list(input_path.glob("*.xlsx")) + list(input_path.glob("*.xls"))
    
    if not excel_files:
        print(f"No Excel files found in '{input_dir}'")
        return
    
    print(f"Found {len(excel_files)} Excel files to process:")
    for file in excel_files:
        print(f"  - {file.name}")
    
    print("\n" + "="*70)
    print("PROCESSING EXCEL FILES")
    print("="*70)
    
    processed_count = 0
    
    for excel_file in excel_files:
        try:
            print(f"\n=== Processing {excel_file.name} ===")
            
            # Process the Excel file (subfolder name will be determined by sheet name)
            processed_data, sheet_name = process_abi_data(str(excel_file), output_path)
            
            print(f"[SUCCESS] Processed {excel_file.name}")
            print(f"  Sheet name: {sheet_name}")
            print(f"  Output subfolder: {output_path / sheet_name}")
            print(f"  Shape: {processed_data.shape}")
            
            processed_count += 1
            
        except Exception as e:
            print(f"[ERROR] Error processing {excel_file.name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n" + "="*70)
    print(f"PROCESSING COMPLETE")
    print(f"Successfully processed {processed_count} out of {len(excel_files)} files")
    print("="*70)


def main():
    """Main function to run the data processing."""
    print("Excel Data Processor for ABI Admissions Data")
    print("="*50)
    
    # Process all Excel files in the england_data directory
    process_all_excel_files()


if __name__ == "__main__":
    main()
