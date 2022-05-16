from .display import ui
from .imap import ImapConnection
from os import path, remove, listdir


def shell():
    """Starts command line app
    """
    # Welcome message
    print('\n--- PyMailOrganizer --- Python command line mail organizer ---\n')

    # Connect to server and fetch emails
    imapConnection = ImapConnection()
    msgs_df = imapConnection.get_emails_from_folder('inbox')

    # Render user interface
    user_interface = ui(msgs_df, imapConnection)

    # Clean up before terminating
    current_dir = path.dirname(path.abspath(__file__))
    files = listdir(current_dir)

    for file in files:
        if file.endswith(".html"):
            remove(path.join(current_dir, file))

    # Termination message
    print('\nThank you for using PyMailOrganizer!\n')


if __name__ == '__main__':
    shell()