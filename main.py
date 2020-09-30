import ConnectorManager

def main():
    manager = ConnectorManager.ConnectorManager("imap.gmail.com", "Config.ini")
    manager.PeriodicallyFetchEmailsFromGmailAndStoreThemAsJsonFiles()

if __name__ == '__main__':
    main()
