# _Ideco PortScanner REST API_

### _Description:_

A REST API developed for scanning ports of remote host.

---

### _Usage:_

_**`START:`**_
Run `python api.py` in the command line.

_**`METHODS:`**_

* `GET`
      
      # Python3 code
      address, begin_port, end_port = '74.125.205.105', 75, 150  # Example (IP address of www.google.com)
      response = requests.get(
          f'http://localhost:9090/scan/{address}/{begin_port}/{end_port}'
      )
          
      # curl -X GET -H 'Accept: */*' -H 'Connection: keep-alive' http://localhost:9090/scan/"<STRING: ADDRESS_REMOTE_HOST>"/<INT: BEGIN_PORT>/<INT: END_PORT>

_**`TESTS:`**_
Run `python tests.py` in the command line.

---

### _Required:_

See the file `requirements.txt`

---

### _Commentaries:_

Also, if you have other additional tasks that you need to complete, write to 
me in Telegram (`@ivanenkogrigory`). I will gladly try to make them. Thanks.

### _Author:_ 

**Ivanenko Grigoriy, Ural State Federal University, 2021.**
