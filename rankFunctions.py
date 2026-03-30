import pandas as pd
import os
import shutil
from pathlib import Path

#WORKING ON IT:
#works for EACH star aka row in the csv
def rankStar(star, sigma, i):

    PMRApred = star['PMRApred']
    PMDecpred = star['PMDecpred']
    PMRA = star['PMRA']
    PMRAerr = star['PMRAerr']
    PMDec = star['PMDec']
    PMDecerr = star['PMDecerr']
    Vrpred = star['Vr(pred)']
    Vrobs = star['Vr(obs)']
    Vrerr = star['Vrerr']
    RVsrc = star['RVsrc']

    p = 0
    #check conditions
    if (abs(PMRApred - PMRA)/PMRAerr < sigma):
        p+=1
    if (abs(PMDecpred - PMDec)/PMDecerr < sigma):
        p+=1
    if ((abs(Vrpred - Vrobs)/Vrerr < sigma) | (pd.notna(RVsrc))):
        p+=1
    return p

def rankCSV(filepath, singlefile=False):
    points = []
    hostname = Path(filepath).stem
    star_csv = pd.read_csv(filepath)

    #iterate through csv rows and store point values
    for i, star in star_csv.iterrows():
        p = rankStar(star, 3, i)
        points.append(p)
    #sort rows
    print(points)
    star_csv['rank_score'] = points #gemini, debug
    star_csv = star_csv.sort_values(by='rank_score', ascending=False)

    #save file
    if (singlefile==True):
        file = f"./{hostname}_friends/{hostname}_rank.csv"
        star_csv.to_csv(file, index=False)
    else:
        file = f"./FindFriends_rank/{hostname}_rank.csv"
        star_csv.to_csv(file, index=False)

def test():
    rankCSV(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\TOI-6448_friends\TOI-6448.csv', True)

test()
