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

Author: Computational Social Scientist
Date: 2025
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import glob


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
