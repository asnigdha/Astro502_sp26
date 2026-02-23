#simple cuts
#run with: python run_known_cluster.py
#used Gemini to debug
#imports
import Comove
import pandas as pd
import os
import shutil

# ## Define the inputs:
# ##An target star name searchable on simbad. If coordinates are used, it will just be used as the default results directory
hostname = 'TOI-2876'
star_csv = pd.read_csv(f"./{hostname}_friends/TOI-2876.csv")

PMRApred = star_csv['PMRApred']
PMDecpred = star_csv['PMDecpred']
PMRA = star_csv['PMRA']
PMRAerr = star_csv['PMRAerr']
PMDec = star_csv['PMDec']
PMDecerr = star_csv['PMDecerr']

#used help from https://stackoverflow.com/questions/29725932/deleting-rows-with-python-in-a-csv-file
star_csv = star_csv[abs(star_csv.PMRApred - star_csv.PMRA) < 3] #3 is arbitrary
star_csv = star_csv[abs(star_csv.PMDecpred - star_csv.PMDec) < 3]

file = f"./{hostname}_friends/TOI-2876_cut.csv"
star_csv.to_csv(file, index=False)