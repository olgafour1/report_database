import pickle
import re
import os
from pdf2image import convert_from_path
import pytesseract
import pandas as pd
from pdfreader import medicalDb
import difflib


with open('records.pickle', 'rb') as handle:
    records = pickle.load(handle)

report_dir="attachments"
sarcoma_codes_dir="/home/sotorios/PycharmProjects/report_database/sarcoma_codes"

def get_report_ids(report_dir):
    report_info=[]
    for pdf_file in os.listdir(report_dir):
        basename= (os.path.splitext(os.path.basename(pdf_file))[0])
        report_info.append([basename,os.path.join(report_dir,pdf_file)])
    return report_info

def get_sarcoma_subtypes(pdf_dir):

    text = ""
    regex_per_page=[r"(?<=Appendix A: List of codes to be included as Soft Tissue Sarcomas)(.*)(?=\sAuthor: MF/SV/RG/SSCRG)",
            r"(.*)(?=\sAuthor: MF/SV/RG/SSCRG)",
            r"(.*)(?=\sAppendix B: Full list of codes discussed with decisions)"]
    for pdf_file,regex in zip(os.listdir(pdf_dir), regex_per_page):
        images = convert_from_path(os.path.join(pdf_dir, pdf_file))
        for image in images:
            m = re.search(regex, str(pytesseract.image_to_string(image)), re.MULTILINE | re.DOTALL)
            text+= m.group(1).lower()

    df =  pd.DataFrame((element for element in text.split("|")), columns=["subtype"])
    df.subtype=df.subtype.apply(lambda x: x.replace("\n"," "))
    df.subtype=df.subtype.apply(lambda x: ''.join([i for i in x if not i.isdigit()]))
    return df

config = {
  'user': 'root',
  'password': 'sarcoma',
  'host': '127.0.0.1'
}
TABLES = {}


TABLES['patients'] = (
    "CREATE TABLE `patient_info` ("
     "  `patient_no` INT(11) AUTO_INCREMENT,"
    "   `patient_id` VARCHAR(15),"
    "   `lab_no` VARCHAR(100),"
    "   `gender`  enum('M','F'),"
    "   `age` INT(11) ,"
    "   `grade` INT(5),"
    "   `rough_diagnosis` TEXT,"
    "   `positivity` TINYTEXT,"
    "   `negativity` TINYTEXT,"
    "   `report_file` VARCHAR(100) NOT NULL,"
    "    UNIQUE KEY (`report_file`),"
    "    PRIMARY KEY (`patient_no`)"
    ") ENGINE=InnoDB")


TABLES['report_files'] = (
    "CREATE TABLE `report_files` ("
    "  `report_patient_id` varchar(15) NOT NULL,"
    "  `patient_info_path` varchar(100) NOT NULL,"
    "   PRIMARY KEY (`report_patient_id`),"
    "   FOREIGN KEY (`patient_info_path`)"
    "   REFERENCES `patient_info` (`report_file`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")

TABLES['codes'] = (
    "CREATE TABLE `codes` ("
    "   `code_no` int(11) AUTO_INCREMENT,"
    "   `code_id` int(5),"
    "   `subtype` TEXT ,"
    "    PRIMARY KEY (`code_no`)"
    ") ENGINE=InnoDB")

insert_patients_statement=("INSERT INTO patient_info"
               "(patient_id,lab_no,gender,age,grade,rough_diagnosis,"
               "positivity,negativity,report_file) "
               "VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s)")

# insert_reports_statement=("INSERT INTO report_files (report_patient_id,patient_info_path) VALUES (%s,%s)")
#
# insert_codes_statement=("INSERT INTO codes (code_id,subtype) VALUES (%s,%s)")
#
# report_info=get_report_ids(report_dir)



with open('codes.pickle', 'rb') as handle:
    codes = pickle.load(handle)


records=pd.DataFrame(records)
records[5] = records[5].apply(lambda x: x.replace("\n", " ") if x is not None else x)
rough_diagnosis=(records[5].values.tolist())
print (codes["subtype"].values.tolist())
for d in rough_diagnosis:

    print (d)
    print ("##################")
    if d is not None:
        for code in codes["subtype"].values.tolist():
            if code in d:
                print (code)


#
# insert_patients=medicalDb(config=config, tables=TABLES, database="test", record=records, insert_statement=insert_patients_statement).create_medical_records()
# insert_reports=medicalDb(config=config, tables=TABLES, database="test", record=report_info, insert_statement=insert_reports_statement).create_medical_records()
# insert_codes=medicalDb(config=config, tables=TABLES, database="test", record=codes.values.tolist(), insert_statement=insert_codes_statement).create_medical_records()