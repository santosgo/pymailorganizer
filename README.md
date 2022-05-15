# PyMailOrganizer

Python command line mail organizer. 

Allows you to browse your emails, read, filter, see a graphic of the top 10 senders and delete what you don't need. I created it initially for my personal use but then I decided to share.

Works only with Gmail and Outlook mail accounts at the moment.


### Installation

You can install the PyMailOrganizer from [PyPI](https://pypi.org/project/pymailorganizer/):

    python -m pip install pymailorganizer

The PyMailOrganizer is supported on Python 3.7 and above.

### Command line options

     d                   Delete by sender
     d[index]            Delete by [index]
     f                   Filter by sender
     g                   Graph top 10 senders
     h                   Help manual
     l                   List last 20 mails
     l[number]           List last [number] mails
     r                   Reload mails from server
     s                   Set number of mails loaded from server
     [number]            Show selected mail on console
     [number] as html    Show selected mail on browser

### Settings

Settings can be changed in the settings.json file. Example:

    {
    "max_default_loaded_mails": 25,
    "remove_urls": false
    }

where

    max_default_loaded_mails = default number of emails loaded from server
    remove_urls = removes all urls from mail messages to improve readability 