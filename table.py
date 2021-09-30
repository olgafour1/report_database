import pickle
from pdfreader import medicalDb

with open('table.pickle', 'rb') as handle:
    df= pickle.load(handle)

df=(df.applymap(lambda x: x.replace("\n"," ")))
df=(df.applymap(lambda x: x[:-2]))
df=df[~df[0].str.contains(" Morphological codes ")]
df=df.reset_index(drop=True)

tumour_category=[" Adipocytic tumours"," Fibroblastic/myofibroblastic tumours",
              " So-called fibrohistiocytic tumours"," Smooth muscle tumours"," Skeletal muscle tumours",
             " Vascular tumours"," Nerve sheath tumours",
              " Chondro-osseus tumours"," Tumours of uncertain differentiation"]
tumour_type=[" Intermediate (locally aggressive)"," Intermediate (rarely metastasizing)", " Malignant"]


df["tumour_category"]=""
category_indices=df.index[df[0].isin(tumour_category) ].tolist()
category_indices.append(df.shape[0])
ranges=list(zip(category_indices[:-1], category_indices[1:]))

for enum,(start, end) in enumerate(ranges):
   df["tumour_category"].iloc[start:end]=df[0].iloc[start]


df["tumour_type"]=""
type_indices=df.index[df[0].isin(tumour_type) ].tolist()
type_indices.append(df.shape[0])
ranges=list(zip(type_indices[:-1], type_indices[1:]))
for enum,(start, end) in enumerate(ranges):
   df["tumour_type"].iloc[start:end]=df[0].iloc[start]
indexes_to_keep = set(range(df.shape[0])) - set(type_indices+category_indices)
df = df.take(list(indexes_to_keep))
print (df.columns)

# config = {
#   'user': 'root',
#   'password': 'sarcoma',
#   'host': '127.0.0.1'
# }
#
# TABLES={}
# TABLES['codes'] = (
#     "CREATE TABLE `tumour_info` ("
#     "   `tumour_subtype` VARCHAR(100),"
#     "   `code` VARCHAR(15),"
#     "   `ct_terminology` TEXT ,"
#     "   `ct_code` VARCHAR(15) ,"
#     "   `tumour_category` VARCHAR(50),"
#     "   `tumour_type` VARCHAR(50) ,"
#     "    PRIMARY KEY (`tumour_subtype`)"
#     ") ENGINE=InnoDB")
#
# insert_sarcoma_info=("INSERT INTO tumour_info (tumour_subtype,code,ct_terminology,"
#                      "ct_code,tumour_category,tumour_type) VALUES (%s,%s,%s,%s,%s,%s)")
#
#
# insert_patients=medicalDb(config=config, tables=TABLES, database="test", record=df.values.tolist(),
# insert_statement=insert_sarcoma_info).create_medical_records()