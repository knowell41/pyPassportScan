# pyPassportScan

A simple script design to return passport details in Json format.

Instructions:

1. make virtual environment to avoid python package conflict

python -m venv <envName>
source <envName>/bin/activate


2. install python dependencies in your virtual environment console by running ./install.sh

3. after installation, refer to this Instruction by Google;
https://cloud.google.com/vision/product-search/docs/before-you-begin

4. By the time you finish the step 3 and downloaded the *.json file, use it as environment variable;

export GOOGLE_APPLICATION_CREDENTIALS="[PATH_TO_JSON_FILE]"


Testing:

import json
from scanlib import Scan

p1 = Scan("./sample.jpg")
p1.read()


it will return result like this;
{'firstname': 'ANNA MARIA', 'lastname': 'ERIKSSON', 'birthday': '2004-08-12', 'gender': 'F', 'country': 'UTO', 'issuingcountry': '', 'passportNumber': 'L898902C3', 'passportExpiration': '2012-04-15', 'idtype': 'P', 'optional_data': 'ZE184226B'}




