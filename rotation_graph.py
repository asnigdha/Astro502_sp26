import pandas as pd
import os
import shutil
from rename import *
import matplotlib.pyplot as plt
from gyrointerp.plotting import *

target_list = pd.read_csv(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\ASTR502_Mega_Target_List - ASTR502_Mega_Target_List.csv')
tars_csv = pd.read_csv(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\TOI-6448_friends\TOI-6448_with_tars.csv')

#variables for relevant columns
hostname = target_list['hostname']
gaia_id = target_list['gaia_dr3_id']
prot = tars_csv['adopted_period']
prot_unc = tars_csv['adopted_period_unc']
bprp = tars_csv['Bp-Rp']

plot1 = plt.scatter(bprp, prot)
gyrointerp.models.reference_cluster_slow_sequence(Teff, model_id, poly_order=7, verbose=True)
# underplot these polynomial fits
model_ids = [
    'α Per', '120-Myr', '300-Myr', 'Praesepe', 'NGC-6811'
]
plt.xlabel('Bp-Rp')
plt.ylabel('Rotation periods')
plt.show()

#pull csv
#star_csv = pd.read_csv(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\TOI-6448_friends\TOI-6448.csv')
# ---------- Rotation Period (Prot) vs Color (Bp-Rp) Plot ----------



#     try:
#         # Selection: radial distance, velocity limits, and convergence cuts
#         zz2 = np.where((sep3d.value < searchradpc.value) & (Gchi2 < vlim.value) &
#                        (sep.degree > 1e-5) & (Cangle.degree > convergcut))[0]
        
#         # Sort by Gchi2 for plotting order (best candidates on top)
#         yy2 = zz2[np.argsort((-Gchi2)[zz2])] if zz2.size > 0 else np.array([], dtype=int)

#         if yy2.size == 0:
#             print("DEBUG: Prot vs Bp-Rp plot selection empty; skipping.")
#         else:
#             figname = outdir + targname.replace(" ", "") + "_rot_color.png"
#             fig, ax1 = plt.subplots(figsize=(12, 8))
            
#             # Extract target_list - Ensure 'prot' exists in your dictionary/table 'r'
#             # If your rotation column name is different, update 'prot' here
#             prot_all = np.array(r['prot'])
#             bprp_all = np.array(r['Bp-Rp'])
            
#             # 1. Plot the 'Field' or background stars in the background
#             # Only plot stars that have an actual rotation period measurement
#             valid_prot = np.where(~np.isnan(prot_all))[0]
#             ax1.scatter(bprp_all[valid_prot], prot_all[valid_prot], 
#                         s=5, marker='.', c='gray', alpha=0.3, label='Field Stars')

#             # 2. Loop through selected candidates (yy2) to plot with specific symbology
#             ccc = None
#             for idx in yy2:
#                 if np.isnan(prot_all[idx]): 
#                     continue
                
#                 # Dynamic sizing based on 3D distance
#                 msize = (17 - 12.0 * (sep3d[idx].value / searchradpc.value))**2
#                 mcolor = Gchi2[idx]
#                 medge = 'black'
#                 mzorder = 7
                
#                 # Shape based on RUWE (standard for Gaia binary/quality flag)
#                 mshape = 'o' if (r['ruwe'][idx] < 1.2) else 's'

#                 # Blue edge for stars that are RV comoving
#                 if rvcut is not None:
#                     if (not np.isnan(RV[idx])) and (np.abs(RV[idx] - Gvrpmllpmbb[idx, 0]) <= rvcut):
#                         medge = 'blue'
                
#                 sc = ax1.scatter(bprp_all[idx], prot_all[idx],
#                                  s=msize, c=mcolor, marker=mshape, 
#                                  edgecolors=medge, zorder=mzorder,
#                                  vmin=0.0, vmax=vlim.value, cmap='cubehelix_r')
#                 ccc = sc

#             # 3. Add the Target/Center star for reference (if it has a prot)
#             # You might need to adjust where you get the target's Bp-Rp and Prot
#             # ax1.plot(target_bprp, target_prot, 'rx', markersize=18, mew=3, label=targname)

#             # Formatting
#             ax1.set_xlabel(r'$G_{BP} - G_{RP}$ (mag)', fontsize=20)
#             ax1.set_ylabel(r'Rotation Period (days)', fontsize=20)
#             ax1.set_yscale('log')  # Rotation plots are often clearer on a log scale
            
#             # Custom Legend
#             ax1.scatter([], [], c='white', edgecolors='black', marker='o', s=100, label='RUWE < 1.2')
#             ax1.scatter([], [], c='white', edgecolors='black', marker='s', s=100, label='RUWE $\geq$ 1.2')
#             ax1.scatter([], [], c='white', edgecolors='blue', marker='o', s=100, label='RV Comoving')
#             ax1.legend(loc='upper right', fontsize=12)

#             if ccc is not None:
#                 cb = plt.colorbar(ccc, ax=ax1)
#                 cb.set_label('$\Delta V_{tan}$ (km/s)', fontsize=16)

#             ax1.grid(True, which="both", ls="-", alpha=0.2)
#             _save_or_skip(fig, figname)

#     except Exception as e:
#         print(f"DEBUG: Prot vs Bp-Rp plot failed ({type(e).__name__}: {e}); continuing.")