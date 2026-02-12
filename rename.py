import os

#function to rename file
def rename_file(star_name, directory_location, filename, end):
    og_path = directory_location + '\\' + filename
    new_path = str(og_path)[:-len(filename)] + str(star_name)+ end
    print(new_path)
    os.rename(og_path, new_path)

#function to rename directory and files inside it
def rename_directory(star_name, directory_location):
    #rename files inside it
    for file in os.listdir(directory_location):
        filename = os.fsdecode(file)
        end = filename[21:]
        print(end)
        rename_file(star_name, directory_location, filename, end)
    name = directory_location[:-8]
    filepath = directory_location + '/' + name #for Windows
    print(filepath +'.csv')
    #rename directory
    os.rename(directory_location, str(star_name)+'_friends')