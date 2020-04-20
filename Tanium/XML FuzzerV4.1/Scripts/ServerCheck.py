import requests
from time import sleep

def Check():

    while True:

        sleep(3)

        checker = """<?xml version="1.0" encoding="utf-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SOAP-ENV:Body>
    <typens:tanium_soap_request xmlns:typens="urn:TaniumSOAP">
      <command>GetObject</command>
      <object_list>
        <groups>
          <group>
            <name>Denial of Service</name>
          </group>
        </groups>
      </object_list>
    </typens:tanium_soap_request>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""

        try:

            requests.packages.urllib3.disable_warnings()

            URL = "https://localhost/soap/"

            print "[*] Sending Check"

            headers = {'Host':'127.0.0.1', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate','DNT':'1', 'Accept-Language': 'en-US,en;q=0.5'}
            
            print requests.post(URL, data=checker, headers=headers, verify=False).text

            print "[*] Tanium Server is ONLINE"


        except:

             print "[*] Tanium Server is OFFLINE"

Check()
