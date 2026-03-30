import Comove
import pandas as pd

target_list = pd.read_csv("C:\\Users\\Snigdha\\Documents\\college\\2025-2026\\ASTR502\\Comove\\ASTR502_Mega_Target_List.csv")

##Set verbose=True to see LOTS of print output
for index, row in target_list.iterrows():
    targname = str(row['hostname'])
    id =  str(row['gaia_dr3_id'])

    # Send the query synchronously
    job = Gaia.launch_job(id)
    # Get the results as an Astropy Table
    results = job.get_results()
    print(results)