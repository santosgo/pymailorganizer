from display import ui
from imap import imap
from os import path, remove, listdir

if __name__ == '__main__':
    # Welcome message
    print('\n--- PyMailOrga --- Python command line mail organizer ---\n')

    # Connect to server and fetch emails
    imapConnection = imap.ImapConnection()
    msgs_df = imapConnection.get_emails_from_folder('inbox')

    # Render user interface
    user_interface = ui(msgs_df, imapConnection)

    # Clean up before terminating
    current_dir = path.dirname(__file__)
    files = listdir(current_dir)

    for file in files:
        if file.endswith(".html"):
            remove(path.join(current_dir, file))

    # Termination message
    print('Thank you for using PyMailOrga!')
