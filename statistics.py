import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_histogram(features, filename):
  n, bins, patches = plt.hist(x=features, bins='auto', color='#0504aa',
                              alpha=0.7, rwidth=0.85)
  plt.grid(axis='y', alpha=0.75)
  plt.xlabel('Age')
  plt.ylabel('Frequency')
  plt.title('Age distribution')
  plt.text(15, 25, r'$\mu={:.2f}, b={:.2f}$'.format(np.mean(features), np.std(features)))
  maxfreq = n.max()

  plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)
  plt.savefig(filename)
  plt.show()


def plot_grouped_data(df, group, field, filename, y_title, x_title, title):

    df = df.groupby([group]).count().reset_index().sort_values(['patient_no'], ascending=True)

    ax = df.plot.barh(x=group ,y=field,figsize=(10,15), color="#0504aa", fontsize=13,  alpha=0.7)
    ax.set_alpha(0.8)
    ax.set_ylabel(y_title, fontsize=20)
    ax.set_xlabel(x_title, fontsize=20)
    plt.title(title,fontsize=20)
    plt.yticks(fontsize=16)
    plt.grid(axis='x', alpha=0.75)
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()



try:
  cnx = mysql.connector.connect(user= 'root',password= 'sarcoma',host='127.0.0.1',database='sarcoma_histo')
  patients = pd.read_sql('SELECT * FROM patient_info', con=cnx)
  plot_grouped_data(patients, "gender", "patient_no", "gender.png", "Gender", "Frequency", "Gender distribution")
  plot_grouped_data(patients, "diagnosis", "patient_no", "diagnosis.png", "Sybtype", "Frequency",
                    "Diagnosis distribution")
  plot_histogram(patients["age"].dropna().values, "age.png")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  cnx.close()


