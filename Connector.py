from abc import ABC, abstractmethod

"""
Base Class for all Connectors

base properties:
1) flag for connected service
2) mail service
3) server

logic:
1) Get Service (abstract method)
"""

class Connector(ABC):
    def __init__(self, smtp_server):
        self.v_mail_service_is_connected = False
        self.__mail_service = None
        self.smtp_server = smtp_server

    @abstractmethod
    def GetService(self):
        pass