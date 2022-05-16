from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tabulate import tabulate
from tqdm import tqdm
import webbrowser

import warnings
warnings.filterwarnings('ignore')


class ui:
    def __init__(self, msgs_df, imap_connection):
        self.imap_connection = imap_connection
        self.account = imap_connection.account
        self.msgs_df = msgs_df
        self.df_to_display = self.msgs_df[['Sender', 'Subject', 'Date']]
        self.__option = ''

        # Print last 10 received mails and total fetched messages
        self.__display_df(10)

        # Render user interface
        while True:

            # Request user option
            self.__option = input('\nOption: ')

            # Quit
            if self.__option == 'q':
                self.__quit()
                break

            # Delete all messages from selected sender
            elif self.__option == 'd':
                self.__delete_by_subject()

            # Delete selected email by dataframe index number
            elif self.__option[0] == 'd' and self.__option[1:].isnumeric():
                self.__delete_by_index()

            # Filter
            elif self.__option == 'f':
                self.__filter_by_sender()

            # Graph top 10 senders
            elif self.__option == 'g':
                self.__graph_top_senders()

            # Help
            elif self.__option == 'h' or self.__option == 'help':
                self.__help()

            # List top 20 mails
            elif self.__option == 'l':
                self.__display_df(20)

            # List selected amount of emails
            elif self.__option[0] == 'l' and self.__option[1:].isnumeric():
                no_of_lines = int(self.__option[1:])
                self.__display_df(no_of_lines)

            # Reload mails from server
            elif self.__option == 'r':
                self. __reload_mails()

            # Set maximum number of loaded mails
            elif self.__option == 's':
                self.__set_max_mails()

            # Show message content by index number
            elif self.__option.isnumeric():
                msg_no = int(self.__option)
                subject = self.msgs_df.loc[msg_no, 'Subject']
                From = self.msgs_df.loc[msg_no, 'Sender']
                body = self.msgs_df.loc[msg_no, 'Body']
                print(f'\n--- Subject: {subject} ')
                print(f'\n--- From: {From} ')
                print(f'\n{body}\n')

            # Show message content by index number as html in the browser
            elif (self.__option.split(' ')[0].isnumeric() and self.__option.split(' ')[1] == 'as' and self.__option.split(' ')[2] == 'html'):
                msg_no = int(self.__option.split(' ')[0])
                # subject = self.msgs_df.loc[msg_no, 'Subject']
                # From = self.msgs_df.loc[msg_no, 'Sender']
                body = self.msgs_df.loc[msg_no, 'Body']
                temp_html = 'temp' + datetime.now().time().strftime('%H%M%S') + '.html'
                with open (temp_html, 'w') as f:
                    f.write(body)
                webbrowser.open(temp_html)
            else:
                print('Invalid option. Try again.')


    def __quit(self):
        # close the connection and logout
        try:
            self.account.close()
            self.account.logout()
        except ConnectionResetError:
            # Connection already closed by peer anyway due to timeout
            pass


    def __delete_by_subject(self):
        selected_sender = input('\nEnter the exact sender from whom you would like to delete ALL emails: ')
        yes_no_delete = input('Are you sure you would like to delete this message (y/n)? ')
        if yes_no_delete == 'y':
            print(f'Selected sender: {selected_sender}')
            filtered_df = self.msgs_df[self.msgs_df.Sender == selected_sender].reset_index()
            rows_filtered = filtered_df.shape[0]
            print(f'\n{rows_filtered} message(s) successfully deleted.\n')
            for i in tqdm(range(0, rows_filtered)):
                self.account.store(filtered_df.loc[i, 'Uid'], "+FLAGS", "\\Deleted")
                self.account.expunge()
            self.df_to_display = self.df_to_display[self.df_to_display.Sender != selected_sender]
            
        else:
            print('Ok, messages were not deleted')


    def __delete_by_index(self):
        msg_no = int(self.__option[1:])
        yes_no_delete = input('Are you sure you would like to delete this message (y/n)? ')
        if yes_no_delete == 'y':
            subject = self.msgs_df.loc[msg_no, 'Subject']
            self.account.store(self.msgs_df.loc[msg_no, 'Uid'], '+FLAGS', '\\Deleted')
            self.account.expunge()
            self.df_to_display.drop(msg_no, inplace=True)
            print(f'\n--- Subject: {subject} ')
            print('\nMessage successfully deleted.\n')
        elif yes_no_delete == 'n':
            print('Ok, message was not deleted')
        else:
            print('Invalid answer.')


    def __filter_by_sender(self):
        by_sender = input('Enter sender to filter by: ')
        df_filtered = self.df_to_display[self.df_to_display.Sender == by_sender]
        pd.set_option('display.max_colwidth', None)
        print(tabulate(df_filtered, headers = 'keys', tablefmt = 'psql'))


    def __graph_top_senders(self):
        sender_count  = self.msgs_df['Sender'].value_counts()
        sender_count = sender_count[:10,]
        plt.figure(figsize=(10,5))
        sns.barplot(sender_count.index, sender_count.values, alpha=0.8)
        plt.title('Top 10 senders to my email', fontsize=14)
        plt.ylabel('Number of Occurrences', fontsize=10)
        plt.xticks(fontsize=8)
        plt.xlabel('Senders', fontsize=10)
        plt.show()


    @staticmethod
    def __help():
        print('\n')
        print(f'd - Delete by sender')
        print(f'd[index] - Delete by [index]')
        print(f'f - Filter by sender')
        print(f'g - Graph top 10 senders')
        print(f'h - Help manual')
        print(f'l - List last 20 mails')
        print(f'l[number] - List last [number] mails')
        print(f'r - Reload mails from server')
        print(f's - Set number of loaded mails from server')
        print(f'[number] - Show selected mail on console')
        print(f'[number] as html - Show selected mail on browser')
        print('\n')

    def __reload_mails(self):
        print('Refreshing emails...\n')
        self.msgs_df = self.imap_connection.get_emails_from_folder('inbox')
        self.df_to_display = self.msgs_df[['Sender', 'Subject', 'Date']]


    def __set_max_mails(self):
        new_max_loaded_mails = input('Set maximum number of loaded emails (press r to reload after this): ')
        if not new_max_loaded_mails.isnumeric():
            print('Only numbers accepted. Try again.')
        else:
            self.imap_connection.max_loaded_mails = int(new_max_loaded_mails)


    def __display_df(self, no_of_lines):
        print(f'\n--- Your last {no_of_lines} received emails ---\n')
        pd.options.display.max_columns = None
        pd.options.display.max_colwidth = None
        self.df_to_display["Subject"] = self.df_to_display["Subject"].str.wrap(50)
        print(tabulate(self.df_to_display.head(no_of_lines), headers = 'keys', tablefmt = 'psql'))
        print(f'Total fetched messages: {self.msgs_df.shape[0]}')
