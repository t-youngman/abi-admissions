"""
CSV Combiner for ABI Admissions Data

This script:
1. Tests if all CSV files with numeric filenames have the same header row
2. Combines all numeric CSV files into one big table
3. Saves the combined data as a new CSV file

Author: Computational Social Scientist
Date: 2025
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import re


def get_numeric_csv_files(directory="processed_data"):
    """
    Get all CSV files whose filename begins with a number.
    
    Args:
        directory (str): Directory to search for CSV files
        
    Returns:
        list: List of Path objects for numeric CSV files
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"Error: Directory '{directory}' does not exist!")
        return []
    
    # Find all CSV files
    all_csv_files = list(directory_path.glob("*.csv"))
    
    # Filter for files that start with a number
    numeric_csv_files = []
    for file in all_csv_files:
        filename = file.stem  # Get filename without extension
        if re.match(r'^\d', filename):  # Check if filename starts with a digit
            numeric_csv_files.append(file)
    
    return sorted(numeric_csv_files)  # Sort for consistent ordering


def test_header_consistency(csv_files):
    """
    Test if all CSV files have the same header row.
    
    Args:
        csv_files (list): List of CSV file paths
        
    Returns:
        tuple: (is_consistent, reference_header, inconsistent_files)
    """
    if not csv_files:
        print("No numeric CSV files found!")
        return False, None, []
    
    print(f"Testing header consistency across {len(csv_files)} numeric CSV files...")
    print("="*70)
    
    reference_header = None
    inconsistent_files = []
    
    for i, file_path in enumerate(csv_files):
        print(f"Checking {file_path.name}...")
        
        try:
            # Read the first row (header) of the CSV file
            df = pd.read_csv(file_path, header=None, nrows=1)
            current_header = df.iloc[0].tolist()
            
            if reference_header is None:
                reference_header = current_header
                print(f"  [OK] Set as reference header ({len(current_header)} columns)")
            else:
                # Compare with reference header
                if current_header == reference_header:
                    print(f"  [OK] Header matches reference ({len(current_header)} columns)")
                else:
                    print(f"  [ERROR] Header does NOT match reference!")
                    print(f"    Reference length: {len(reference_header)}")
                    print(f"    Current length: {len(current_header)}")
                    
                    # Show differences
                    if len(current_header) != len(reference_header):
                        print(f"    Column count mismatch!")
                    else:
                        differences = []
                        for j, (ref, cur) in enumerate(zip(reference_header, current_header)):
                            if ref != cur:
                                differences.append(f"      Column {j}: '{ref}' vs '{cur}'")
                        if differences:
                            print("    Column differences:")
                            for diff in differences[:5]:  # Show first 5 differences
                                print(diff)
                            if len(differences) > 5:
                                print(f"    ... and {len(differences) - 5} more differences")
                    
                    inconsistent_files.append(file_path)
        
        except Exception as e:
            print(f"  [ERROR] Error reading file: {str(e)}")
            inconsistent_files.append(file_path)
    
    is_consistent = len(inconsistent_files) == 0
    
    print("="*70)
    if is_consistent:
        print(f"[SUCCESS] ALL {len(csv_files)} FILES HAVE CONSISTENT HEADERS!")
        print(f"   Reference header has {len(reference_header)} columns")
    else:
        print(f"[WARNING] {len(inconsistent_files)} FILES HAVE INCONSISTENT HEADERS:")
        for file in inconsistent_files:
            print(f"   - {file.name}")
    
    return is_consistent, reference_header, inconsistent_files


def combine_csv_files(csv_files, output_file="combined_abi_data.csv", region_name=None):
    """
    Combine all CSV files into one big table.
    
    Args:
        csv_files (list): List of CSV file paths
        output_file (str): Output filename for combined data
        region_name (str): Region name to add as first column
        
    Returns:
        pd.DataFrame: Combined dataframe
    """
    if not csv_files:
        print("No CSV files to combine!")
        return None
    
    print(f"\nCombining {len(csv_files)} CSV files...")
    print("="*50)
    
    combined_dataframes = []
    total_rows = 0
    
    for i, file_path in enumerate(csv_files):
        print(f"Reading {file_path.name}...")
        
        try:
            # Read the CSV file
            df = pd.read_csv(file_path, header=None)
            
            # Add Region column at the start
            if region_name:
                # Insert a new column at the beginning
                df.insert(0, 'Region', region_name)
                
                # Set the header row value to 'Region'
                if i == 0:  # Only for first file (which has header)
                    df.iloc[0, 0] = 'Region'
                    print(f"  Added 'Region' column with value: '{region_name}'")
            
            # Skip the header row (first row) for all files except the first
            if i > 0:
                df = df.iloc[1:]  # Remove first row (header)
            
            combined_dataframes.append(df)
            total_rows += len(df)
            print(f"  [OK] Added {len(df)} rows (total: {total_rows})")
            
        except Exception as e:
            print(f"  [ERROR] Error reading file: {str(e)}")
            continue
    
    if not combined_dataframes:
        print("No dataframes to combine!")
        return None
    
    # Combine all dataframes
    print(f"\nCombining {len(combined_dataframes)} dataframes...")
    combined_df = pd.concat(combined_dataframes, ignore_index=True)
    
    print(f"[SUCCESS] Successfully combined data!")
    print(f"   Final shape: {combined_df.shape[0]} rows × {combined_df.shape[1]} columns")
    
    # Save the combined data to the same directory as the source files
    if csv_files:
        output_dir = csv_files[0].parent
        output_path = output_dir / output_file
        combined_df.to_csv(output_path, index=False, header=False)
        print(f"   Saved to: {output_path}")
    
    return combined_df


def process_all_subfolders(base_dir="processed_data"):
    """
    Process all subfolders in the base directory.
    For each subfolder, combine all numeric CSV files.
    Then combine all regional files into England.csv
    
    Args:
        base_dir (str): Base directory containing subfolders
    """
    base_path = Path(base_dir)
    
    if not base_path.exists():
        print(f"Error: Base directory '{base_dir}' does not exist!")
        return
    
    # Find all subdirectories
    subfolders = [f for f in base_path.iterdir() if f.is_dir()]
    
    if not subfolders:
        print(f"No subfolders found in '{base_dir}'")
        return
    
    print(f"Found {len(subfolders)} subfolders to process:")
    for folder in subfolders:
        print(f"  - {folder.name}")
    
    print("\n" + "="*70)
    print("PROCESSING SUBFOLDERS")
    print("="*70)
    
    processed_count = 0
    regional_files = []  # Store paths to combined regional files
    
    for subfolder in subfolders:
        try:
            print(f"\n=== Processing subfolder: {subfolder.name} ===")
            
            # Get numeric CSV files from this subfolder
            numeric_files = get_numeric_csv_files(str(subfolder))
            
            if not numeric_files:
                print(f"  No numeric CSV files found in {subfolder.name}, skipping...")
                continue
            
            print(f"  Found {len(numeric_files)} numeric CSV files")
            
            # Test header consistency
            is_consistent, reference_header, inconsistent_files = test_header_consistency(numeric_files)
            
            if not is_consistent:
                print(f"  [WARNING] {len(inconsistent_files)} files have inconsistent headers!")
                print(f"  Continuing with combination anyway...")
            
            # Combine the files with output name matching the subfolder name
            # Pass the subfolder name as the region_name
            output_filename = f"{subfolder.name}.csv"
            combined_df = combine_csv_files(numeric_files, output_filename, region_name=subfolder.name)
            
            if combined_df is not None:
                print(f"  [SUCCESS] Combined data saved as '{output_filename}'")
                print(f"     Total rows: {len(combined_df)}")
                print(f"     Total columns: {len(combined_df.columns)}")
                
                # Store the path to this combined file for later England.csv creation
                regional_file_path = subfolder / output_filename
                regional_files.append(regional_file_path)
                
                processed_count += 1
            
        except Exception as e:
            print(f"  [ERROR] Error processing subfolder {subfolder.name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n" + "="*70)
    print(f"PROCESSING COMPLETE")
    print(f"Successfully processed {processed_count} out of {len(subfolders)} subfolders")
    print("="*70)
    
    # Now combine all regional files into England.csv
    if regional_files:
        print(f"\n" + "="*70)
        print("CREATING ENGLAND.CSV FROM ALL REGIONAL FILES")
        print("="*70)
        
        try:
            england_df = combine_regional_files(regional_files, base_path)
            if england_df is not None:
                print(f"\n[SUCCESS] Created England.csv with {len(england_df)} rows")
        except Exception as e:
            print(f"[ERROR] Error creating England.csv: {str(e)}")
            import traceback
            traceback.print_exc()


def combine_regional_files(regional_files, output_dir):
    """
    Combine all regional CSV files into one England.csv file.
    
    Args:
        regional_files (list): List of paths to regional CSV files
        output_dir (Path): Directory to save England.csv
        
    Returns:
        pd.DataFrame: Combined England dataframe
    """
    if not regional_files:
        print("No regional files to combine!")
        return None
    
    print(f"\nCombining {len(regional_files)} regional files into England.csv...")
    print("="*50)
    
    combined_dataframes = []
    total_rows = 0
    
    for i, file_path in enumerate(regional_files):
        print(f"Reading {file_path.name}...")
        
        try:
            # Read the CSV file
            df = pd.read_csv(file_path, header=None)
            
            # Skip the header row (first row) for all files except the first
            if i > 0:
                df = df.iloc[1:]  # Remove first row (header)
            
            combined_dataframes.append(df)
            total_rows += len(df)
            print(f"  [OK] Added {len(df)} rows (total: {total_rows})")
            
        except Exception as e:
            print(f"  [ERROR] Error reading file: {str(e)}")
            continue
    
    if not combined_dataframes:
        print("No dataframes to combine!")
        return None
    
    # Combine all dataframes
    print(f"\nCombining {len(combined_dataframes)} regional dataframes...")
    england_df = pd.concat(combined_dataframes, ignore_index=True)
    
    print(f"[SUCCESS] Successfully combined regional data!")
    print(f"   Final shape: {england_df.shape[0]} rows × {england_df.shape[1]} columns")
    
    # Save England.csv to the base processed_data directory
    output_path = output_dir / "England.csv"
    england_df.to_csv(output_path, index=False, header=False)
    print(f"   Saved to: {output_path}")
    
    return england_df


def main():
    """Main function to run the CSV combining process."""
    print("CSV Combiner for ABI Admissions Data")
    print("="*50)
    
    # Process all subfolders in the processed_data directory
    process_all_subfolders()


if __name__ == "__main__":
    main()
