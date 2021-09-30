import pytesseract
from pdf2image import convert_from_path,exceptions
import re
import mysql.connector
from mysql.connector import errorcode
import itertools

class pdfReader(object):

    def __init__(self, pdf_path,patient_dir, expressions):
        self.patient_dir = patient_dir
        self.expressions = expressions
        self.pdf_path=pdf_path

    @staticmethod
    def read_pdf(path):
        text=''
        try:
            images=convert_from_path(path)
            for image in images:
                text += str(pytesseract.image_to_string(image))
        except exceptions.PDFPageCountError:
            raise ValueError('Exception: PDFPageCountError for %s' % path)
        return  text


    @staticmethod
    def extract_regex(dir,text, expressions, path):
        matches = []

        for key,expression in zip(dir.keys(),expressions):
                try:
                    if isinstance(expression, list):
                        multiple_arguments=[]
                        for exp in expression:
                            m = re.findall(exp,text, re.MULTILINE | re.DOTALL)
                            multiple_arguments.append(m)
                        multiple_arguments=list(map(''.join, list(itertools.chain(*multiple_arguments))))

                        if  multiple_arguments:

                            matches.append(', '.join(multiple_arguments) if len(multiple_arguments)>2 else multiple_arguments[0])
                            print("Regular expression for {} field: {}  ".format(key, ''.join(multiple_arguments)))
                        else:
                            print("There is no matching regular expression for {} field in file {}".format(key, path))
                            matches.append(None)
                    else:

                        m = re.search(expression, text, re.MULTILINE | re.DOTALL)
                        matches.append(m.group(1).lower())
                        print("Regular expression for {} field: {}  ".format(key, m.group(1).lower()))

                except AttributeError:
                    print("There is no matching regular expression for {} field in file {}".format(key, path))
                    matches.append(None)


        matches.append(path)
        return matches

    def get_patient_record(self):
        medical_report_text=self.read_pdf(self.pdf_path)
        patient_record=self.extract_regex(self.patient_dir,medical_report_text, self.expressions, self.pdf_path)
        return patient_record

class medicalDb(object):

    def __init__(self, database,config, tables, record, insert_statement):
        self.tables=tables
        self.congif=config
        self.database=database
        self.record=record
        self.insert_statement=insert_statement


    @staticmethod
    def connect_to_mysql_server(config):
        try:
                cnx = mysql.connector.connect(**config)
                cursor = cnx.cursor()
        except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Authenticaion error")
                else:
                    print(err)
        else:
                return cnx,cursor

    @staticmethod
    def create_database(cursor,database):
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(database))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

    @staticmethod
    def create_table(cursor, tables):
        for table_name in tables:
            table_description = tables[table_name]
            try:
                print("Creating table {}: ".format(table_name), end='')
                cursor.execute(table_description)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("table already exists.")
                else:
                    print(err.msg)
            else:
                print("Table {} created successfully.".format(table_name))

    @staticmethod
    def insert_records(cursor,cnx,records, insert_statement):

        add_record = insert_statement
        try:
            if any(isinstance(i, list) for i in records):
                cursor.executemany(add_record, records)
                cnx.commit()
            else:
                cursor.execute(add_record, records)
                cnx.commit()
        except mysql.connector.Error as e:
            print ("Error code:", e.errno)
            print ("Error message:", e.msg)


    def create_medical_records(self):

        cnx,cursor=self.connect_to_mysql_server(self.congif)
        try:
            cursor.execute("USE {}".format(self.database))
        except mysql.connector.Error as err:
            print("Database {} does not exists.".format(self.database))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.create_database(cursor, self.database)
                print("Database {} created successfully.".format(self.database))
                cnx.database = self.database
            else:
                print(err)
                exit(1)
        finally:
            self.create_table(cursor, self.tables)
            self.insert_records(cursor, cnx, self.record, self.insert_statement)
            cnx.close()

















