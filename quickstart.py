from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
import base64
import email

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials2.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    return service

    """Get a list of Messages from the user's mailbox.
"""

def ListMessagesMatchingQuery(service, user_id = 'me', query='from:(diiaru@outlook.es) subject:(Test py)'):
    response = service.users().messages().list(userId=user_id, q=query).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
        messages.extend(response['messages'])

    return messages


def ListMessagesWithLabels(service, user_id, label_ids=[]):
    response = service.users().messages().list(userId=user_id, labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id, labelIds=label_ids, pageToken=page_token).execute()
        messages.extend(response['messages'])

    return messages

def GetMessage(service, user_id, msg_id):
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    #print('Message snippet: %s' % message['snippet'])

    return message

def GetAttachments(service, user_id, msg_id, store_dir='./'):
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    for part in message['payload']['parts']:
        if part['filename']:
            # Este proceso busca el id dentro del arbol donde <<filename>> contenga el nombre del adjunto y lo guardará en una variable.
            att_id = part['body']['attachmentId']
            # Seguidamente, ejecutará el proceso para obtener los metadatos del adjunto
            att = service.users().messages().attachments().get(userId=user_id, messageId=msg_id, id=att_id).execute()
            print(att)
            data = att['data']
            # Despues de-codificará en base64 para finalmente guardar el archivo en el path especificado.
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            path = ''.join([store_dir, part['filename']])

            f = open(path, 'wb')
            f.write(file_data)
            f.close()

if __name__ == '__main__':
    service = main()
    messages = ListMessagesMatchingQuery(service)
    print(type(messages))
    print(len(messages))
    msg_id = messages[0]['id']
    msg = GetMessage(service, 'me', msg_id)
    GetAttachments(service, 'me', msg_id)
    """
    print(msg_id)
    """
