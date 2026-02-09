import Comove
import pandas as pd
import os


## Define the inputs:
##An target star name searchable on simbad. If coordinates are used, it will just be used as the default results directory
data = pd.read_csv(r'C:\Users\Snigdha\Documents\college\2025-2026\ASTR502\Comove\ASTR502_Mega_Target_List - ASTR502_Mega_Target_List.csv')

hostname = data['hostname']
gaia_id = data['gaia_dr3_id']
ra = data['ra']
dec = data['dec']
rv = data['st_rv']
err_rv =  data['st_e_rv']

i = 1151
targname = gaia_id[i]
print(hostname[i])

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
output_location = Comove.findfriends(str(targname),float(radvel),velocity_limit=vlim,search_radius=srad,radec=rd,output_directory=None,verbose=False,showplots=False)
#os.rename(output_location, str(hostname[i])+'_friends'))
