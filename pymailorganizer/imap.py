import email
from email.header import decode_header
import getpass
from halo import Halo
import imaplib
import json
from os import path
import pandas as pd
import re
from tqdm import tqdm


class ImapConnection:
    """
    Establishes a IMAP connection to an email account
    """
    def __init__(self):
        """
        Asks the credentials on the terminal, connects and gets the account's data
        If the email is not on gmail or outlook, the host and port are requested as well
        Gets default maximum number of loaded emails from settings.json
        """

        self.__get_settings()
        self.max_loaded_mails = self.__settings['max_default_loaded_mails']

        self.__creds = self.__get_creds()

        if self.__creds['email_user'][-10:] == '@gmail.com':
            host = 'imap.gmail.com'
            port = 993
        elif self.__creds['email_user'][-12:] == '@outlook.com':
            host = 'imap-mail.outlook.com'
            port = 993
        else:
            host = input('Enter imap host: ')
            port = input('Enter imap port: ')

        spinner = Halo(text='Connecting', spinner='dots')
        spinner.start()

        self.account = imaplib.IMAP4_SSL(host, port)
        self.account.login(self.__creds['email_user'], self.__creds['email_pass'])

        spinner.stop()
        print(f'\nConnected to mail account')


    def __get_creds(self):
        """
        Requests the credentials in the terminal

        Returns:
            dict: credentials dictionary
        """
        email_user = input('User: ')
        email_pass = getpass.getpass()

        creds = {
            'email_user': email_user,
            'email_pass': email_pass
        }

        return creds


    def __get_settings(self):
        """
        Gets the settings from the settings.json file

        Raises:
            FileNotFoundError: if the settings.json file is not found in the parent path of the program
        """
        current_dir = path.dirname(path.abspath(__file__))
        settings_path = current_dir + '/settings.json'
        if path.exists(settings_path):
            with open(settings_path, 'r') as f:
                json_settings = f.read()
            self.__settings = json.loads(json_settings)
        else:
            raise FileNotFoundError("File settings.json not found")


    def get_emails_from_folder(self, folder):
        """
        Fetches emails from a folder
        The maximum number of retrieved emails at program start comes from the file settings.json
        but it can be changed from within the user interface menu with option 's'

        Args:
            folder (str): mailbox folder like 'inbox"

        Returns:
            dataframe: dataframe containing all emails
        """
        
        print(f'Fetching {self.max_loaded_mails} emails...\n')
        msgs = self.__get_messages_from_folder(folder)
        df = self.__msgs_to_df(msgs)

        return df


    def __get_messages_from_folder(self, folder):
        """
        Fetches emails from a given email folder like inbox

        Args:
            folder (str): mailbox folder like 'inbox'

        Returns:
            list: list of tuples containing a message ID and a message object
        """
        self.account.select(folder)
        data = self.account.search(None, 'ALL')

        mail_ids = data[1]
        id_list = mail_ids[0].split()

        print(f'\nYou have {len(id_list)} emails in your inbox\n')

        first_email_id = int(id_list[-1])
        last_email_id = int(id_list[-self.max_loaded_mails-1])

        msgs = []

        for id in tqdm(range(first_email_id, last_email_id, -1)):

            data = self.account.fetch(str(id), '(RFC822)' )

            for response_part in data:
                arr = response_part[0]
                if isinstance(arr, tuple):
                    try:
                        msg = email.message_from_string(str(arr[1], 'utf-8'))
                    except:
                        msg = email.message_from_string(str(arr[1], 'unicode_escape'))
                    msgs.append((str(id), msg)) # will generate a list of tuples id, message

        return msgs


    def __msgs_to_df(self, msgs):
        """
        Transforms list of tuples containing message ID and message object into a pandas dataframe

        Args:
            msgs (list): list of tuples containing a message ID and a message object

        Returns:
            dataframe: dataframe containing all emails
        """
        data_list = []

        for msg in msgs:
            email = msg[1] # msg(0) is the ID
            subject = self.__get_header_component(email, 'subject')
            From = self.__get_header_component(email, 'From').split('<')[0].split(',')[0].replace('"', '').strip()
            date = self.__get_header_component(email, 'date')
            body = self.__get_body(email)
            if self.__settings['remove_urls']:
                body = self.__remove_urls(body)
            else:
                pass
            uid = msg[0]
            data_list.append([subject, From, date, body, uid])

        col_list = ['Subject', 'Sender', 'Date', 'Body', 'Uid']
        df = pd.DataFrame(data_list, columns=col_list)
        df['Date'] = pd.to_datetime(df['Date'], infer_datetime_format=True, format='%d/%b/%Y, %H:%M:%S')

        return df


    def __get_header_component(self, msg, component):
        """
        Gets the header component for a message

        Args:
            msg (obj): email message object
            component (str): header component

        Returns:
            str: component content
        """
        try:
            component, encoding = decode_header(msg[component])[0]
            if isinstance(component, bytes):
                # if it's a bytes, decode to str
                if encoding:
                    component = component.decode(encoding)
                else:
                    component = component.decode()
        except:
            component=''
        return component


    def __remove_urls(self, text):
        """
        Removes urls from a string

        Args:
            text (str): any given string

        Returns:
            string: string without url links
        """
        return re.sub(r'https?://\S+', '', text)


    def __get_body(self, msg):
        """
        Gets the body from a list an email object

        Args:
            msg (obj): email object

        Returns:
            str: email body
        """
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    charset = part.get_content_charset()
                    body_part = part.get_payload(decode=True)
                    try:
                        body += body_part.decode(charset)
                    except:
                        body += body_part.decode('unicode_escape')
                    return body
        else:
            body_part = msg.get_payload()
            if isinstance(body_part, bytes):
                body = body_part.decode()
            else:
                body = body_part

        return body
