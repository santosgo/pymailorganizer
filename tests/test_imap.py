from imap import imap
import pandas as pd


def test_get_messages():
    imapConnection = imap.ImapConnection()
    msgs_df = imapConnection.get_emails_from_folder('inbox')
    print(msgs_df.head())