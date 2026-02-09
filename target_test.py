import Comove
import pandas as pd

print('Debug 0')
## Define the inputs
##An target star name searchable on simbad. If coordinates are used, it will just be used as the default results directory
target_list = pd.read_csv("C:\\Users\\Snigdha\\Documents\\college\\2025-2026\\ASTR502\\Comove\\ASTR502_Mega_Target_List.csv")

##This line runs the entire code. Set showplots=True to interactively plot, otherwise they are only saved as pngs
##Set verbose=True to see LOTS of print output
for index, row in target_list.iterrows():
    id =  str(row['gaia_dr3_id'])
    targname = str(row['hostname'])

    ##Alternative is to use coordinates, default is [None,None] in which case the targname is used to get coordinates
    rd = [None,None]
    #rd = ['12 40 45.9694160957', '-21 52 21.831891557']

    print('Debug 1')    

    ##input target star radial velocity to calulate 3D space velocities
    job = Gaia.launch_job(id)
    # Get the results as an Astropy Table
    results = job.get_results()
    print(results)
    # radvel=row[''] ##km/s
    

    # ##Neighbour velocity difference limit, and on sky search radius
    # vlim=5.0 ##km/s
    # srad=25.0 ##parsecs (spherical radius around target)

    # output_location = Comove.findfriends(targname,radvel,velocity_limit=vlim,search_radius=srad,radec=rd,output_directory=None,verbose=False,showplots=False)