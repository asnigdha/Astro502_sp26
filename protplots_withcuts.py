import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gyrointerp as gi
from pathlib import Path
from matplotlib.lines import Line2D

def protvteff(csv_path, sigma=5, singlefile=False):
    star_csv = pd.read_csv(csv_path)
    hostname = Path(csv_path).stem.replace("_with_tars", "")
    
    if star_csv.empty:
        return

    # --- THE "GENEROUS" PARAMETERS ---
    # Since your model (pred) is off from the data (obs) by ~12 mas/yr,
    # we increase the floor to capture the bulk motion mismatch.
    pm_floor = 5.0  # Increased floor to 5.0 mas/yr
    rv_floor = 2.0  

    plt.figure(figsize=(10, 7))

    for i, star in star_csv.iterrows():
        # Padded Error calculation
        err_ra_total = np.sqrt(star['PMRAerr']**2 + pm_floor**2)
        err_dec_total = np.sqrt(star['PMDecerr']**2 + pm_floor**2)
        
        # Calculate Sigmas
        sig_ra = abs(star['PMRApred'] - star['PMRA']) / err_ra_total
        sig_dec = abs(star['PMDecpred'] - star['PMDec']) / err_dec_total
        
        # PM Pass: If RA and Dec are within sigma
        pm_pass = (sig_ra < sigma) and (sig_dec < sigma)
        
        # RV Pass
        err_vr_total = np.sqrt(star['Vrerr']**2 + rv_floor**2)
        rv_pass = (pd.isna(star['RVsrc'])) or \
                  (abs(star['Vr(pred)'] - star['Vr(obs)']) / err_vr_total < sigma)

        # Plotting
        if pm_pass and rv_pass:
            plt.scatter(star['teff'], star['adopted_period'], marker='.', color='black', alpha=0.7, zorder=3)
        elif pm_pass and not rv_pass:
            plt.scatter(star['teff'], star['adopted_period'], marker='x', color='red', s=40, zorder=2)
        else:
            plt.scatter(star['teff'], star['adopted_period'], marker='o', edgecolors='blue', facecolors='none', s=40, alpha=0.3, zorder=1)

    # Host Star
    plt.scatter(star_csv['teff'].iloc[0], star_csv['adopted_period'].iloc[0], 
                marker='*', s=300, color='gold', edgecolors='black', label='Host Star', zorder=10)

    # Gyro Models
    range_t = np.arange(3000, 11000)
    ages = [100, 200, 300, 400, 500, 600, 700, 800, 900]
    for age in ages:
        try:
            md = gi.models.slow_sequence(range_t, age, poly_order=7)
            plt.plot(range_t, md, alpha=0.3)
        except: continue

    plt.xlabel(r'$T_{eff}$ [K]')
    plt.ylabel('Rotation periods [days]')
    plt.title(f"Rotation vs Teff: {hostname}")
    plt.xlim(7000, 3000)
    plt.ylim(0, 35)
    
    legend_elements = [
        Line2D([0], [0], marker='.', color='w', label='Passes Cuts', markerfacecolor='black', markersize=10),
        Line2D([0], [0], marker='x', color='w', label='Fails RV', markeredgecolor='red', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Fails PM', markeredgecolor='blue', markerfacecolor='none', markersize=8),
        Line2D([0], [0], marker='*', color='w', label='Host Star', markerfacecolor='gold', markeredgecolor='black', markersize=12)
    ]
    plt.legend(handles=legend_elements, loc='upper left')

    folder = Path(f"./FindFriends_prot")
    folder.mkdir(parents=True, exist_ok=True)
    plt.savefig(folder / f"{hostname}_prot_cuts.png", dpi=300)
    plt.close()

def main():
    src_dir = Path(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\new_tars')
    for filepath in src_dir.glob('*.csv'):
        print(f"Processing {filepath.name}...")
        # We use sigma=5 and a 5.0 floor. This means a star can be up to 
        # ~25 mas/yr away from the prediction and still pass.
        protvteff(filepath, sigma=5)

if __name__ == "__main__":
    main()