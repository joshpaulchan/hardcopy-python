"""
@name       downloader.py
@version    0.1.0
@desc       Multi-threaded Google Drive download manager.
"""

import os
import io
import time
import shutil
from threading import BoundedSemaphore
from concurrent.futures import ThreadPoolExecutor

import httplib2
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload
from oauth2client import client, tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.hardcopy/credentials.json
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'hardcopy'

# taken from Drive API Quickstart (https://developers.google.com/drive/v3/web/quickstart/python)
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = os.path.join(os.path.expanduser('~'), '.hardcopy')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'credentials.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        # if flags:
        credentials = tools.run_flow(flow, store)
        # else: # Needed only for compatibility with Python 2.6
        #     credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def clear_credentials():
    """
    Clears the credentials stored in the credentials folder.
    """
    credential_dir = os.path.join(os.path.expanduser('~'), '.hardcopy')
    if os.path.exists(credential_dir):
        shutil.rmtree(credential_dir)

class Downloader(object):
    
    def __init__(self):
        """Constructor"""
        # google
        self.credentials = get_credentials()
        
        self.http = self.credentials.authorize(httplib2.Http())
        self.drive = discovery.build('drive', 'v3', http=self.http)
    
    def download(self, file_id, output_path, opts=None):
        """
        Downloads the file with the given `file_id`.
        
        @param  {str}   file_id     the file_id of the file to download
        @param  {dict}  opts        download options
        @return {None}  
        """
        if opts is None:
            opts = {}
            
        req = self.drive.files().export(fileId=file_id, mimeType=opts.get('mime_type', 'application/pdf'))
        
        print("Downloading: " + output_path)
        try:
            # create if it doesn't exist
            file_handler = open(output_path, 'x+b')
            file_handler.close()
        except FileExistsError:
            pass
        
        # apparently this way is trash 9http://stackoverflow.com/questions/38830800/google-drive-python-api-export-never-completes/41643652#41643652
        # write into buffer
        # fh = io.BytesIO()
        # downloader = MediaIoBaseDownload(fh, req)
        # print('hey')
        # done = False
        # while done is False:
        #     status, done = downloader.next_chunk()
        #     print("Download %d%%." % int(status.progress() * 100))
        
        try:
            resp = req.execute(http=self.http)
        except Exception as e:
            print(e)
            return
            
        # write to file
        with open(output_path, 'wb') as file:
            file.write(resp)

INSTANCE = Downloader()

def download(file_id, output_path, opts=None):
    """Wrapper for `INSTANCE.download()`"""
    INSTANCE.download(file_id, output_path, opts)
