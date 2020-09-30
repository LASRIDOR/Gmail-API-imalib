# Gmail-API-imalib

# Gmail API- 
# periodically every 10 seconds fetch unread emails from Gmail and store them as JSON files
For each iteration get all emails that are marked as unread and fetch them.
For each email:

1. Marked the email as read at the Gmail inbox (In order not to fetch them again on the next iteration) .
2. Save the email as JSON file - File name should be - email time + Message-ID
3. Email JSON file structure:
     a. Sender (name and email address)
     b. Receiver (my email address)
     c. Subject (as is)
     d. Body (string of the body)
# Connector – imaplib
In order to accomplish the mail reading task i’ll make use of the imaplib Python module.
imaplib is a built in Python module, hence you don’t need to install anything. You simply need to import the module.
inorder to login to Gmail using Python. we need a mail server, a username and password. In this case, since we are trying to login to Gmail, our mail server would be either imap.gmail.com or smtp.gmail.com. 
Ito read the incoming mail your incoming mail server would be imap.gmail.com and ito send mail then your outgoing mail server would be smtp.gmail.com.
Hence, our mail server is imap.google.com.
Username and password are your Gmail username and password which will be in the Config.ini file.
Email address and password should be like that:
YourEmailAddress + "@gmail.com"
YourPassword
Smtp_server =  imap.gmail.com
Imap is a 3rd party product so inorder to get access to the Gmail account the user has to give permission through the Gmail Account
INTERNET MESSAGE ACCESS PROTOCOL - VERSION 4rev1:
https://tools.ietf.org/html/rfc3501

# GUIDE - enable "less secure apps" on Gmail Account
1.	Go to your (Google Account).
2.	On the left navigation panel, click Security.
3.	On the bottom of the page, in the Less secure app access panel, click Turn on access.

If you don't see this setting, your administrator might have turned off less secure app account access (check the instruction above).
4.	Click the Save button.
This less secure apps enable gives anybody that has you email address and password an access to your Gmail account
# Config file
The only Iteraction this program has with the out world is thru Config file in order to set the Connector settings you need to make an Config file
Guide: the config file name should be: Config.ini
Location: Program Location
Content:
 [Credentials]
email = "email address"@gmail.com
Password "password"

[Path]
address = "C:\......"

[IterationPeriod]
intervals = integer value in seconds
PAY ATTENTION:
Config file can be change while the program (with different email or path or interval according to your decision) is running and should stay at the same location during the whole time (the config will be checked at each iteration of the program)
Incase of problem with the connection the program will solve it with events (can be fixed at any time).
Incase of problem with the path JSON file will be saved at the Lost Mails folder where the program is saved.
# Extras
Inorder to periodically fetch every 10 seconds I user RepeatedTimer class which can be forced to stop or start at any time .
In addition you can change to interval time at any time while running.
Some extra: for future use you can add to the program a long running timer in addition to the interval which will set the overall time running
For Future use
Add an option to change server
Add option to give path to the config file


