import numpy as np
import pandas as pd
import os
import shutil
from rename import *
import matplotlib.pyplot as plt
import gyrointerp as gi
from pathlib import Path

def protvteff(csv_path, singlefile=False):
    tars_csv = pd.read_csv(csv_path)
    
    # Use the 'csv_path' passed into the function
    hostname = Path(csv_path).stem
    hostname = hostname.replace("_with_tars", "")
    
    prot = tars_csv['adopted_period']
    Teff = tars_csv['teff']

    # --- Plotting Logic ---
    plt.figure(figsize=(8, 6)) # Create a new figure for each CSV
    plt.scatter(Teff, prot, marker='.', color='black')
    
    range_t = np.arange(3000, 11000)
    ages = [100, 200, 300, 400, 500, 600,700, 800, 900]
    for age in ages:
        md = gi.models.slow_sequence(range_t, age, poly_order=7)
        plt.plot(range_t, md, label=f'{age} Myr')
    #gemini debug --v
    if Teff.empty or prot.empty:
        print(f"Skipping {hostname}: No data found in columns.")
        return
    plt.scatter(Teff.iloc[0], prot.iloc[0], marker='x', s=200, color='red', label='Host Star', zorder=5)
    plt.xlabel(r'$T_{eff}$ [K]')
    plt.ylabel('Rotation periods [days]')
    plt.legend()
    plt.xlim(7000, 3000)
    plt.ylim(0, 30)
    
    # --- Saving Logic ---
    if singlefile:
        folder = Path(f"./{hostname}_friends")
    else:
        folder = Path(f"./FindFriends_prot")
        
    folder.mkdir(parents=True, exist_ok=True)
    plot = folder / f"{hostname}_prot.png"
    
    # CORRECT WAY TO SAVE THE IMAGE:
    plt.savefig(plot, dpi=300)
    plt.close() # CRITICAL: Close the plot to free up memory

def main():
    # Source of your data
    src_dir = Path(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\new_tars')
    
    if not src_dir.exists():
        print(f"Error: {src_dir} does not exist!")
        return

    # Loop through the CSVs in the source directory
    for filepath in src_dir.glob('*.csv'):
        print(f"Processing {filepath.name}...")
        protvteff(filepath)

    print('Plots created!')

main()
