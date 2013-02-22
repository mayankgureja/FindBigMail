FindBigMail
===========

An IMAP program that allows Gmail users to delete their largest mails and merge folders, written in Python

How To Run
----------

Just launch findBigMail.py. There are no parameters.


Description
-----------

findBigMail.py is a IMAP utility written in Python. It uses the imaplib library to connect to a user's Gmail account and allows them to perform a couple of different functions.

1. Find Big Mail:
In this mode, the user is run through their Gmail INBOX, looking for the largest emails that they have. One-by-one, the details for the largest email is displayed and the user is given the option to delete it. Then, the next largest email is displayed.

2. Merge Folders:
In this mode, the user can merge 2 folders (or labels) into 1. No new folders are created, as that seems to not be allowed through IMAP. All messages are moved to the destination folder.

A menu is shown to the user when the program is launched. Simply follow that to enter either of the 2 modes described above.