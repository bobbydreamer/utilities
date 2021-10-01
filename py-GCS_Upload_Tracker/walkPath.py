"""
Walks folder and subfolders and creates markdown and html files with links pointing to gcs bucket

# GSUTIL Command
# gsutil -m cp -r ./tmp gs://<<enter-your-bucket-name>> 

Note : Using markdown2 as markdown is getting stuck converting large files
"""

import os
from fnmatch import fnmatch
import pathlib
from pathlib import Path
from datetime import datetime
import markdown2

def walkFolders(root, pattern):

    list_of_files = []
    for path, subdirs, files in os.walk(root):
        for name in files:        
            if fnmatch(name, pattern):
                # print(os.path.join(path, name))
                # print(pathlib.PurePath(path, name).as_posix()) #as_posix() makes the slash forward
                list_of_files.append(pathlib.PurePath(path, name).as_posix())

    # get list of ffiles with size
    files_with_size = [ (file_path, os.stat(file_path).st_size) 
                        for file_path in list_of_files ]
    return files_with_size

def main():        

    #### Initializations
    bucket = '<<enter-your-bucket-name>>'
    root = './tmp'
    pattern = "*"

    fnGCSList = bucket+'--gcsList.md'
    cURI = Path(fnGCSList)
    fnHttpList = bucket+'--httpList.md'
    cHttp = Path(fnHttpList)

    # Read walkPath.txt to get input parameters    
    if Path('walkPath.txt').is_file(): # file exists
        print('Reading input from walkPath.txt')
        temp = [line.rstrip() for line in open('walkPath.txt')]
        for i in temp:
            key, val = i.split('=')
            exec(key + '=val')
            print('{}={}'.format(key, val))
    else:
        print('Input file was missing, created a sample walkPath.txt. Please update it and re-run')
        temp = ['bucket=bucket-name', 'pattern=*', 'root=.']
        print('Writing input file walkPath.txt')
        with open('walkPath.txt', 'w') as f:
            f.write('\n'.join(temp))
        exit()

    files_with_size = walkFolders(root, pattern)
    total_size = 0

    #### If file already exists read them into list
    gcsList = []
    if cURI.is_file(): # file exists
        # Markdown seems to add additional <br/> tag, so removing the existing one
        gcsList = [line.rstrip().replace('<br />','')+'    ' for line in open(fnGCSList)] #rstripping a adding blanks is for markdown
        # with open(fnGCSList) as f:
        #     gcsList = f.readlines().rstrip('\n')

    httpList = []
    if cHttp.is_file(): # file exists
        httpList = [line.rstrip()+'    ' for line in open(fnHttpList)]
        # with open(fnHttpList) as f:
        #     httpList = f.readlines()

    URIs = []
    links = []

    if len(files_with_size) > 0 :        
        #### Append new information from  bucket
        curDate = datetime.now().strftime("%Y-%m-%d")
        URIs.append('### '+curDate+' ----------------------------------------------------------------------    ')
        URIs.append('Total files {} of size {}mb     '.format(len(files_with_size), round(total_size,2)))
        links.append('### '+curDate+' ----------------------------------------------------------------------    ')
        links.append('Total files {} of size {}mb     '.format(len(files_with_size), round(total_size,2)))

        # Iterate over list of tuples i.e. file_paths with size
        # and print them one by one        
        print('\nAll files and sizes')
        total_size = 0
        for file_path, file_size in files_with_size:
            total_size += round(file_size/(1024*1024),2)
            print('{0:15s} --> {1}'.format(str(round(file_size/(1024*1024),2))+'mb', file_path))

            file_path = str(file_path)
            filesize = str(round(file_size/(1024*1024),2))+'mb'
            # URIs.append(filesize+' -- gsutil cp gs://'+bucket+'/'+file_path+' .    ')
            URIs.append('``{0:15s} -- gsutil cp gs://{1}/{2} .  ``   <br />'.format(filesize, bucket, file_path))
            if file_path[-1] != '/':
                links.append(filesize+' -- ['+file_path+'](https://storage.cloud.google.com/'+bucket+'/'+file_path+')    ')
            else:
                links.append('-- '+bucket+'/'+file_path+'    ')        

        print('Total files {} of size {}mb'.format(len(files_with_size), round(total_size,2)))                


        #### Append earlier info with new info
        if len(gcsList) > 0:
            URIs.extend(gcsList)

        if len(httpList) > 0:
            links.extend(httpList)

        #### Write .md file
        print('\nWriting .md files')
        with open(fnGCSList, 'w') as f:
            f.write('\n'.join(URIs))

        with open(fnHttpList, 'w') as f:
            f.write('\n'.join(links))

        print('Converting GSUTIL .md file to markdown')

        #### Open GSUTIL file and convert to markdown
        with open(fnGCSList, 'r') as f:
            text = f.read()
            html = markdown2.markdown(text)

        print(' -Writing GSUTIL html file to markdown')
        with open(fnGCSList[:-3]+'.html', 'w') as f:
            f.write(html)

        print('Converting http .md file to markdown')

        #### Open HTTPs file and convert to markdown
        with open(fnHttpList, 'r') as f:
            text = f.read()
            html = markdown2.markdown(text)

        print(' -Writing htpp html file to markdown')
        with open(fnHttpList[:-3]+'.html', 'w') as f:
            f.write(html)

        print('HTML output files generated')        
        print('* {}'.format(fnGCSList[:-3]+'.html'))
        print('* {}'.format(fnHttpList[:-3]+'.html'))

        print('\n Now you can issue below GSUTIL command upload files')
        print('\n    gsutil -m cp -r {} gs://{} \n'.format(root,bucket))
        print('\n After upload completes you can delete the files in folder {}\n'.format(root))


if __name__ == "__main__":
    main()