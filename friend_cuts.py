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
def simpleCut(filepath, sigma, singlefile=False):
    star_csv = pd.read_csv(filepath)
    hostname = Path(filepath).stem

    PMRApred = star_csv['PMRApred']
    PMDecpred = star_csv['PMDecpred']
    PMRA = star_csv['PMRA']
    PMRAerr = star_csv['PMRAerr']
    PMDec = star_csv['PMDec']
    PMDecerr = star_csv['PMDecerr']
    Vrpred = star_csv['Vr(pred)']
    Vrobs = star_csv['Vr(obs)']
    Vrerr = star_csv['Vrerr']
    RVsrc = star_csv['RVsrc']


    #used help from https://stackoverflow.com/questions/29725932/deleting-rows-with-python-in-a-csv-file
    star_csv = star_csv[abs(PMRApred - PMRA)/PMRAerr < sigma] #3 is arbitrary
    star_csv = star_csv[abs(PMDecpred - PMDec)/PMDecerr < sigma]

    #radial velocity cuts
    star_csv = star_csv[(abs(Vrpred - Vrobs)/Vrerr < sigma) | RVsrc.isna()]

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
            simpleCut(file_path, 3)
        else:
            print(str(file_path) + ' is not found.')
            problemList.append(file_path)
    return np.array(problemList)

#WORKING ON IT:
def sortStar(directory, comovingFolder, otherFolder, howMany=1):
    for filepath in Path(directory).rglob('*'):
        if (Path(filepath).is_file()):
            star_csv = pd.read_csv(filepath)
            if (len(star_csv)==howMany):
                new_path = otherFolder / filepath.name
                filepath.rename(new_path)
            else:
                new_path = comovingFolder / filepath.name
                filepath.rename(new_path)

#works for EACH star aka row in the csv
def rankStar(star):
    print(star)
    p = 0
    #check conditions
    # if (star['']):
    #     p+=1
    # if ():
    #     p+=1
    # if ():
    #     p+=1
    return p

def rankCSV(CSV, singlefile=False):

    points = []
    star_csv = pd.read_csv(filepath)

    #iterate through csv rows and store point values
    for i, star in star_csv.iterrows():
        p = rankStar(star)
        points.append()
    #sort rows
    star_csv.sort_values(by='points', ascending=False)

    #save file
    if (singlefile==True):
        file = f"./{hostname}_friends/{hostname}_rank.csv"
        star_csv.to_csv(file, index=False)
    else:
        file = f"./FindFriends_rank/{hostname}_rank.csv"
        star_csv.to_csv(file, index=False)
    

def main():

    cuts_folder = Path(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\FindFriends_cuts')
    cuts_folder.mkdir(parents=True, exist_ok=True)

    # # NOTE: replace path for ur code
    problem = CutCSVs(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\ALL_CSVS')
    # print(problem)

    # create sort folders (Gemini + me)
    # 1. Define your path
    # Use 'r' before the string to handle Windows backslashes correctly
    single_folder = cuts_folder / 'singleStars'
    comoving_folder = cuts_folder / 'comovingStars'

    # 2. Create the directory
    # exist_ok=True prevents an error if the folder already exists
    single_folder.mkdir(parents=True, exist_ok=True)
    comoving_folder.mkdir(parents=True, exist_ok=True)

    print(f"Directory created at: {single_folder}")
    print(f"Directory created at: {comoving_folder}")

    sortStar(cuts_folder, comoving_folder, single_folder)
    print('Stars Sorted 1 Time!')

    #ranks
    rank_folder = Path(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\FindFriends_rank')
    rank_folder.mkdir(parents=True, exist_ok=True)

    #other cuts

    #sort again

    #etc

#main()