from pdfreader import pdfReader, medicalDb
import os
import json



pdf_path="attachments"
json_dir="json"
pdf_files=os.listdir(pdf_path)

#
dir = {"Patient": None,
       "Lab No": None,
       "Sex": None,
       "Age": None,
       " Grade": None,
       "Diagnosis": None,
       "Positive for":None,
       "Negative for": None,
       "Report_file":None}

expressions = [r"\D(\d{6,10})\D",
               "(\d{4}(:?/)\d{2})",
                r'(?:Sex|\d{1,2} (?:YEAR-OLD|YEAR OLD|year old))+ (\w)',
               r'(\d{1,2}) (?:YEAR-OLD|YEAR OLD|year old)+',
               "grade (\d{1,2})",
               "(?:features are consistent with|features (?:would be|are) in keeping with|The features are of|The features suggest|features (?:favor|favoring))"
               "(.*?(,|\.))",
                [r'(?:\s*positive for\s*)((?:[a-zA-Z0-9&._$-]+)(?:(?:,|\sand)\s*[a-zA-Z0-9&_$/-]+(?:\s*(?!and)(?:[a-zA-Z0-9&_$/-]+)))*)',
                    r'(?:expression\sof)\s*(?:focal\s|multifocal\s|nuclear|cytoplasmic\s)*([a-zA-Z0-9-_$/]+)',
                 r'(?:strong\s)((?!strong\s|moderate\s|focal\s|multifocal\s|nuclear|cytoplasmic\s|expression\s)[a-zA-Z0-9-_$-/]+)(?:\s*expression)*',
                 ],
                [r'\s*negative for\s*([^.]*)']
               ]

records=[]


for pdf_file in pdf_files:
    file_name=(os.path.splitext(os.path.basename(pdf_file))[0])
    record=pdfReader(pdf_path=os.path.join(pdf_path,pdf_file),patient_dir=dir, expressions=expressions).get_patient_record()
    dictionary = dict(zip(dir, record))
    json_object=json.dumps(dictionary, indent=4)
    with open(os.path.join(json_dir,file_name+".json"), "w") as outfile:
        outfile.write(json_object)
    records.append(record)




