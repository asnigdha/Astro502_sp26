#simple cuts
#run with: python run_known_cluster.py
#used Gemini to debug
#imports
import Comove
import numpy as np
import pandas as pd
import os
import shutil
from pathlib import Path

# ## parameters: filepath for each csv
def simpleCut(filepath, singlefile=False):
    star_csv = pd.read_csv(filepath)
    hostname = Path(filepath).stem

    PMRApred = star_csv['PMRApred']
    PMDecpred = star_csv['PMDecpred']
    PMRA = star_csv['PMRA']
    PMRAerr = star_csv['PMRAerr']
    PMDec = star_csv['PMDec']
    PMDecerr = star_csv['PMDecerr']

    #used help from https://stackoverflow.com/questions/29725932/deleting-rows-with-python-in-a-csv-file
    star_csv = star_csv[abs(star_csv.PMRApred - star_csv.PMRA)/star_csv.PMRAerr < 3] #3 is arbitrary
    star_csv = star_csv[abs(star_csv.PMDecpred - star_csv.PMDec)/star_csv.PMDecerr < 3]

    if (singlefile==True):
        file = f"./{hostname}_friends/{hostname}_cut.csv"
        star_csv.to_csv(file, index=False)
    else:
        file = f"./FindFriends_cuts/{hostname}_cut.csv"
        star_csv.to_csv(file, index=False)

def CutCSVs(directory):
    problemList = []
    for file_path in Path(directory).rglob('*'):
        if (Path(file_path).is_file()):
            simpleCut(file_path)
        else:
            print(str(file_path) + ' is not found.')
            problemList.append(file_path)
    return np.array(problemList)

#WORKING ON IT:
#def deleteSingleStar(directory):
#    for 

#replace path for ur code
problem = CutCSVs(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\ALL_CSVS')
print(problem)
