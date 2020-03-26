import subprocess
import glob
import os

partition = '/'
archive_folder = 'Images/Archive/'
threshold = 40

df = subprocess.Popen(['df', '-h'], stdout=subprocess.PIPE)

for line in df.stdout:
    splitline = line.decode().split()
    if splitline[5] == partition:
        
        freespace = splitline[3][:-1]
        factor = splitline[3][-1]
        
        file_count = 0 
        
        print freespace + factor + ' free.'
        
        if factor == 'G':
            print('1GB+ of free space, no action required.')
        elif factor == 'M' and freespace >= 20:
            print('20M+ of free space, no action required.')
        else:
            print('Low disk space. Clearing old archive images...')
            
            file_count = len([name for name in os.listdir(archive_folder) if not os.path.isdir(name)])
            
            files_to_remove = file_count * 0.25
            
            # Collect list of files in the directory
            list_of_files = glob.glob(archive_folder + '*')
            
            i=0
            
            while i < files_to_remove:
                
                print('get oldest file')
                oldest_file = min(list_of_files, key=os.path.getctime)
                
                print(oldest_file)
                
                print('remove oldest file.')
                os.remove(oldest_file)
                
                list_of_files.remove(oldest_file)            
                
                i=i+1
