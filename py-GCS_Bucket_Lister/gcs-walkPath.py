"""
Listing objects in buckets and creating 2 sets of files 
1. GSUTIL Command .md file with respective HTML file
2. Authenticated HTTPS link .md file with respective HTML file

-- NOTE --
1. Update project_id
2. Specify Service Account JSON Path 
3. Bucket name
"""

import os
import json
from pathlib import Path
from datetime import datetime
import markdown2

from google.cloud import storage
from google.oauth2 import service_account

project_id = '<<Project-id>>'

with open('<<GCS-Service-Account.JSON') as source:
    sa_info = json.load(source)

storage_credentials = service_account.Credentials.from_service_account_info(sa_info)
storage_client = storage.Client(project=project_id, credentials=storage_credentials)

def list_blobs_with_prefix(bucket_name, prefix, delimiter=None):
    """
    Lists all the blobs in the bucket that begin with the prefix.
    """

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter)

    filesList = []
    print("Blobs:")
    for blob in blobs:
        print(blob.name)
        filesList.append(blob.name)

    if delimiter:
        print("Prefixes:")
        for prefix in blobs.prefixes:
            print(prefix)
    
    return filesList


def main():

    #### Initializations
    bucket = '<<Bucket-name>>'
    fnGCSList = bucket+'--gcsList.md'
    cURI = Path(fnGCSList)
    fnHttpList = bucket+'--httpList.md'
    cHttp = Path(fnHttpList)

    os.remove(fnGCSList)
    os.remove(fnHttpList)

    #### Read from bucket
    filesList = list_blobs_with_prefix(bucket, '', '')
    URIs = []
    links = []

    if len(filesList) > 0 :        
        #### Append new information from  bucket
        curDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        URIs.append(curDate+' ----------------------------------------------------------------------    ')
        links.append(curDate+' ----------------------------------------------------------------------    ')

        for f in filesList:
            URIs.append('gsutil cp gs://'+bucket+'/'+f+' .    ')
            if f[-1] != '/':
                links.append('['+f+'](https://storage.cloud.google.com/'+bucket+'/'+f+')    ')
            else:
                links.append(bucket+'/'+f+'    ')

        # print(URIs)
        # print(links)

        #### Write .md file
        with open(fnGCSList, 'w') as f:
            f.write('\n'.join(URIs))

        with open(fnHttpList, 'w') as f:
            f.write('\n'.join(links))

        #### Open GSUTIL file and convert to markdown
        with open(fnGCSList, 'r') as f:
            text = f.read()
            html = markdown2.markdown(text)

        with open(fnGCSList[:-3]+'.html', 'w') as f:
            f.write(html)

        #### Open HTTPs file and convert to markdown
        with open(fnHttpList, 'r') as f:
            text = f.read()
            html = markdown2.markdown(text)

        with open(fnHttpList[:-3]+'.html', 'w') as f:
            f.write(html)

if __name__ == "__main__":
    main()