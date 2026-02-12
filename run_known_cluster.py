#run with: python run_known_cluster.py
#imports
import Comove
import pandas as pd
import os

#functions

#function to rename file
def rename_file(star_name, directory_location, filename, end):
    og_path = directory_location + '\\' + filename
    new_path = str(og_path)[:-len(filename)] + str(star_name)+ end
    #print(new_path)
    os.rename(og_path, new_path)

#function to rename directory and files inside it
def rename_directory(star_name, directory_location):
    #rename files inside it
    for file in os.listdir(directory_location):
        filename = os.fsdecode(file)
        file_location = str(directory_location)+'/'+ filename
        end = filename[22:]
        rename_file(star_name, directory_location, file, end)
        name = directory_location[:-8]
    filepath = directory_location + '/' + name #for Windows
    print(filepath +'.csv')
    #rename directory
    new_directory_location = os.rename(directory_location, str(hostname[i])+'_friends')

## Define the inputs:
##An target star name searchable on simbad. If coordinates are used, it will just be used as the default results directory
data = pd.read_csv(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\ASTR502_Mega_Target_List - ASTR502_Mega_Target_List.csv')

#variables for relevant columns
hostname = data['hostname']
gaia_id = data['gaia_dr3_id']
ra = data['ra']
dec = data['dec']
rv = data['st_rv']
err_rv =  data['st_e_rv']

i = 505
targname = gaia_id[i]
print(hostname[i])
#print('RV: ' + str(rv[i]))

##Alternative is to use coordinates, default is [None,None] in which case the targname is used to get coordinates
#rd = [None,None]
rd = [ra[i], dec[i]]#['217.3920159', '39.7903991']
print(rd)

##input target star radial velocity to calulate 3D space velocities
radvel= rv[i] ##km/s
err_radvel = err_rv[i]
print(radvel)
print(err_radvel)

##Neighbour velocity difference limit, and on sky search radius
vlim=5.0 ##km/s
srad=25.0 ##parsecs (spherical radius around target)

##This line runs the entire code. Set showplots=True to interactively plot, otherwise they are only saved as pngs
##Set verbose=True to see LOTS of print output
output_location = Comove.findfriends(str(targname),float(radvel),velocity_limit=vlim,search_radius=srad,radec=rd,output_directory=None,verbose=True,showplots=False)

#rename directory and files using hostname
rename_directory(hostname[i], output_location)

print('Part 1 Done!')

#Cuts

#calculate error