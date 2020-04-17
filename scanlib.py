import sys
import io
import os
import json
import time
from PIL import Image
import pandas as pd

##Factor used to crop passport Image to retrive MRZ region##
crop_factor = 0.223
############################################################
class Scan:
    def __init__(self, filepath):
        self.filepath = filepath

    def read(self):
        crop = self.crop()
        data = self.read_mrz(crop)
        data = json.dumps(data)
        data_json = json.loads(data)
        return data_json

    def convert(self, code):

        data = pd.read_csv(str(os.getcwd()) +"/ctrycode.csv")
        val1 = ""

        for i in range(len(data)):
            test_str = data['CODE'][i]
            if code == test_str:
                val1 = data['COUNTRY'][i]
                break
        return val1

    def bday(self, inp):
        val = ""
        if inp <= 18:
            val = "20"
        else:
            val = "19"
        return val

    def constructor(self, dictionary):
        mrzL1 = ""
        mrzL2 = ""
        dictionary_len = len(dictionary)
        mrz_elem_len = {}
        mrz_final = {}
        for i in range(dictionary_len):
            mrz_elem_len[str(i)] = len(dictionary[str(i)])
        sumL = 0
        index_flag = []
        for i in range(dictionary_len):
            sumL+=mrz_elem_len[str(i)]
            if sumL == 44:
                index_flag.append(i)
                sumL = 0
        try:
            if index_flag[0] == 0 and index_flag[1] == 1:
                if mrz_elem_len["0"] == 44:
                    mrzL1 = dictionary["0"]
                if mrz_elem_len["1"] == 44:
                    mrzL2 = dictionary["1"]
            else:
                for i in range(index_flag[0]+1):
                    mrzL1 += dictionary[str(i)]
                for i in range(index_flag[0]+1, index_flag[1]+1):
                    mrzL2 += dictionary[str(i)]
            mrzL1 += "\n"
            return mrzL1, mrzL2
        except:
            print("index flag error")

    def crop(self):
        from PIL import Image
        from PIL import ImageFont
        from PIL import ImageDraw
        in_file = self.filepath
        out_file = 'crop.jpg'
        img = Image.open(in_file)
        width, height = img.size
        x_start = 0
        x_end = width
        y_start = height - int(height*crop_factor)
        y_end = height
        cropped = img.crop((x_start, y_start, x_end, y_end))
        cropped.save(out_file)
        return out_file

    def read_mrz(self, mrz_in):
        from google.cloud import vision
        client = vision.ImageAnnotatorClient()

        with io.open(mrz_in, 'rb') as image_file:
            content = image_file.read()

        image = vision.types.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        wordList = []
        i = 0
        for text in texts:
            if i == 0:
               i=0
            else:
                wordList.append('{}'.format(text.description))
            i+=1


        mrz_entry = {}
        for i in range(len(wordList)):
            mrz_entry[str(i)] = wordList[i]
        mrz_td = Scan.constructor(self, mrz_entry)
        from mrz.base.countries_ops import is_code
        from mrz.checker.td3 import TD3CodeChecker
        mrz_td3 = mrz_td[0] + mrz_td[1]
        td3_check = TD3CodeChecker(mrz_td3, check_expiry=True)

        def print_txt(title, value):
            print(title.ljust(20), value)

        fields = td3_check.fields()
        if str(fields.document_type) != "P":
            sys.stderr.write("not a passport\n")

        optional_data = str(fields.optional_data)
        firstname_format = str(fields.name)
        surname_format = str(fields.surname)
        document_type = str(fields.document_type)

        name_format = str(fields.surname) + " " + str(fields.name)
        sex_raw = str(fields.sex)
        bday_raw = str(fields.birth_date)
        bday_yr_raw = bday_raw[0:2]
        try:
            bday_yr_format = bday(int(bday_yr_raw))
        except:
            bday_yr_raw = bday_raw[1:2]
            bday_yr_raw = "0" + bday_yr_raw
            bday_yr_format = Scan.bday(self, int(bday_yr_raw))
        bday_yr_format = bday_yr_format + str(bday_yr_raw)
        nationality_raw = str(fields.nationality)
        country_raw = str(fields.country)
        country_format = Scan.convert(self, country_raw)


        bday_format = str(bday_yr_format) + "-" + bday_raw[2:4] + "-" + bday_raw[4:6]
        passport_no_raw = str(fields.document_number)
        expiry_raw = str(fields.expiry_date)
        expiry_format = "20" + expiry_raw[0:2] + "-" + expiry_raw[2:4] + "-" + expiry_raw[4:6]




        payload1 = {"firstname": firstname_format,
                   "lastname": surname_format,
                   "birthday": bday_format,
                   "gender": sex_raw,
                   "country": nationality_raw,
                   "issuingcountry": country_format,
                   "passportNumber": passport_no_raw,
                   "passportExpiration": expiry_format,
                   "idtype": document_type,
                   "optional_data": optional_data}
        data = payload1
        return data
