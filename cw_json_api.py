#!/usr/bin/env python3.7
# written by Brian Foley for Midwest Data internal use only

import json
import requests
import base64

# couple things are hardcoded specifically for mwdata - look in __init__ for hardcoded 'bfoley@mwdata' and close_ticket for hardcoded '696'
# search strings are found here: https://developer.connectwise.com/Products/Manage/REST

class cwjsonapi:

    def __init__(self, cwCompanyName, cwPublicKey, cwPrivateKey, clientID, **kwargs):
    
        """Create cwjsonapi object

        Args:
            cwCompanyName (str): Connectwise company abbreviation
            cwPublicKey (str): API public Key
            cwPrivateKey (str): API private Key
            clientID (str): client ID as provided by https://developer.connectwise.com/ClientID
            
        Keyword Args:
            url (str): URL for API endpoint, defaults to https://api-na.myconnectwise.net/v4_6_release/apis/3.0/
            headers (dict): Override request headers
        
        Returns:
            cwjsonapi object
        """
        self.cwCompanyName = cwCompanyName
        self.cwPublicKey = cwPublicKey
        self.cwPrivateKey = cwPrivateKey
        self.clientID = clientID

        self.cwToken = cwCompanyName + "+" + cwPublicKey + ":" + cwPrivateKey
        self.cwToken = base64.b64encode(self.cwToken.encode("utf-8")).decode()

        if ("url" in kwargs):
            self.cwUrl = kwargs["url"]
        else:
            self.cwUrl = "https://api-na.myconnectwise.net/v4_6_release/apis/3.0/"
        
        if ("headers" in kwargs):
            self.requestOptions["headers"] = kwargs["headers"]
        else:
            self.cwHeaders = {"Authorization":"Basic " + self.cwToken,
                "clientID":self.clientID,
                "Content-Type":"application/json"}
                     
        # make a quick request to ensure all is setup OK
        try:
            r = requests.get(self.cwUrl + "company/contacts?pageSize=1&childconditions=communicationItems/value='bfoley@mwdata.net'", headers=self.cwHeaders)
            r.raise_for_status()
        except:
            print(r.text)
            raise

    def get_cust_id_by_email(self, contactEmail):
        """Get the internal company ID based on email provided

        Args:
            contactEmail (str): an email account that belongs to a customer in Connectwise
        """
        baseUrl = self.cwUrl + "company/contacts/"
        payload = {"pageSize": "1",
            "childconditions": "communicationItems/value='" + contactEmail + "'"
            }
        try:
            r = requests.get(baseUrl, params=payload, headers=self.cwHeaders)
            r.raise_for_status()
        except:
            print(r.text)
            raise

        result = r.json()
        try:
            cwCompanyId = str(result[0]["company"]["id"])
            return cwCompanyId
        except:
            return

    def get_backup_tickets(self, cwCompanyId):
        """Get the 50 most recent backup tickets

        Args:
            companyId (str): the INTERNAL company ID in Connectwise, which is a number not related to the customer number or MACC ID
        """
        
        baseUrl = self.cwUrl + "service/tickets/"
        payload = {"pageSize": "50", 
            "page": "Last", 
            "orderBy": "dateEntered desc",
            "conditions": "company/id=" + cwCompanyId + " and board/name='Backup Tickets'"
            }
        try:
            r = requests.get(baseUrl, params=payload, headers=self.cwHeaders)
            r.raise_for_status()
        except:
            print(r.text)
            raise

        result = r.json()
        
        tickets = result
        return tickets

    def get_all_open_backup_tickets(self):
        """Get all tickets on the backup board with status 'New' or 'In Progress' - max results 1000

        """
        
        baseUrl = self.cwUrl + "service/tickets/"
        payload = {"pageSize": "1000", 
            "page": "Last", 
            "orderBy": "dateEntered desc",
            "conditions": "board/name='Backup Tickets' and (status/name='New' or status/name='In Progress')"
            }
        try:
            r = requests.get(baseUrl, params=payload, headers=self.cwHeaders)
            r.raise_for_status()
        except:
            print(r.text)
            raise

        result = r.json()
        
        tickets = result
        return tickets
        
    def get_ticket(self, cwTicket):
        """Gets a ticket
        
        Args:
            cwTicket: A ticket number
        """
        
        baseUrl = self.cwUrl + "service/tickets/"
        payload = {"pageSize": "1", 
            "conditions": "id="+str(cwTicket)
            }
        try:
            r = requests.get(baseUrl, params=payload, headers=self.cwHeaders)
            r.raise_for_status()
        except:
            print(r.text)
            raise
        result = r.json()
        ticket = result[0]
        return ticket
               
    def close_ticket(self, cwTicket):
        """Sets a ticket status to '>Closed'
        
        Args:
            cwTicket: A ticket number
        """
                
        baseUrl = self.cwUrl + "service/tickets/"+str(cwTicket)
        # TODO: write a function to obtain the unique status ID for the board the ticket lives on - e.g. get_status_id('>Closed') to avoid hardcoded 696 that only exists on a specific board
        payload = [{'op': 'replace', 'path': 'status/id', 'value': 696}] # note - this is a list
        try:
            r = requests.patch(baseUrl, json=payload, headers=self.cwHeaders)
            r.raise_for_status()
        except:
            print(r.text)
            raise
        
        return
        
    def add_internal_note(self, cwTicket, msg):
        """Adds an internal note to a ticket
        
        Args:
            cwTicket: A ticket number
            msg: The contents of the note
        """
                        
        baseUrl = self.cwUrl + "service/tickets/"+str(cwTicket)+"/notes"
        payload = { 'text': str(msg),
                'internalAnalysisFlag': 'true'
            }
        try:
            r = requests.post(baseUrl, json=payload, headers=self.cwHeaders)
            r.raise_for_status()
        except:
            print(r.text)
            raise
        
        return