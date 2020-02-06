from flask import Flask, render_template, request
from werkzeug import secure_filename
import pandas as pd
import psycopg2
import json
from matplotlib import pyplot as plt 
from datetime import datetime, date
import time
import dateutil.parser


try:
    connection = psycopg2.connect(user = "postgres",
                                  password = "root",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "test")

    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
 
except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)


app = Flask(__name__)

insertion_count = 0;


separateformat = [];

def readanyotherformat(filename,s):
   formatfromupload = s;
   filetoupload = filename

   filenametoread =filename + "." +s;
   
   if formatfromupload == "XLSX" or formatfromupload == "xlsx":
      df = pd.read_excel(filenametoread)

      firstname = df['FirstName'];
      lastname = df['LastName']
      Phoneno = df['Phone No']

      for index, row in df.iterrows(): 
         print (row['FirstName'], row['LastName'],row['Phone No'])

         ##postgres_insert_query = "INSERT INTO fresh_candidate_upload (fname, lname, phone_no)  VALUES (%s,%s,%s)",row['FirstName'],row['LastName'],row['Phone No']

         cursor.execute("INSERT INTO fresh_candidate_upload (fname,lname,phone_no,upload_time,current_stage,new_stage) VALUES (%s, %s,%s,%s,%s,%s)", (row['FirstName'],row['LastName'],row['Phone No'],'NOW()','Rejected','Rejected'))         
         #cursor.execute(postgres_insert_query)
         connection.commit()
         count = cursor.rowcount
         insertion_count = count;
        
         #print (count, "Record inserted successfully into mobile table")
   return count;   

   if formatfromupload == "CSV" or formatfromupload == "csv":
      df = read_csv(filenametoread);
      print(df)
      



@app.route('/') 
def hello_world():
   return render_template('file_upload.html')


@app.route('/enterdetails',methods = ['POST', 'GET']) 
def enterdetails():  

   if request.method == 'GET':

      print("GET CALLED")
      myvar = request.args.get('pno');
      cursor.execute("select fname,lname,phone_no from fresh_candidate_upload where phone_no= %s", [myvar])
      candidate_records = cursor.fetchall() 
      return render_template('candidate_details.html',candidate_info = candidate_records)   
   
   if request.method == 'POST':
      print("POST CALLED")

      competancy = request.form.get('competancyname');
      location = request.form.get('location_select');

      Fname = request.form.get('FirstName');
      Lname = request.form.get('LastName');
      Phoneno = request.form.get('phone');
      Idate = request.form.get('idate');
      selectcstatus = request.form.get('currentstatus');
      rcurrstatus = request.form.get('cstatus');
      selectnstatus = request.form.get('newstatus'); 
      rnewstatus = request.form.get('nstatus');

      if(rcurrstatus == "rejected" or rnewstatus == "rejected"):
         Final_Status = "Closed"         
      else:
        Final_Status = "Yet to Process"

      if(selectcstatus == "Technical Interview" and rcurrstatus == "selected"):
         selectnstatus = "manager round";
         Final_Status = "Yet to Process"

      elif(selectcstatus == "manager round" and rcurrstatus == "selected"):
         selectnstatus = "HR compensation round";
         Final_Status = "Yet to Process"

      elif(selectcstatus == "HR compensation round" and rcurrstatus == "selected"):
         selectnstatus = "Benchmarking";
         Final_Status = "Yet to Process"

      elif(selectcstatus == "Benchmarking" and rcurrstatus == "selected"):
         selectnstatus = "Headroom";
         Final_Status = "Yet to Process"

      elif(selectcstatus == "Headroom" and rcurrstatus == "selected"):
         selectnstatus = "Offer rollout";
         Final_Status = "Yet to Process"

      elif(selectcstatus == "Offer rollout" and rcurrstatus == "selected"):
         selectnstatus = "offer accepted";
         Final_Status = "Yet to Process"

      elif(selectcstatus == "offer accepted" and rcurrstatus == "selected"):
         selectnstatus = "to be onboarded";
         Final_Status = "Yet to Process"

      elif(selectcstatus == "to be onboarded" and rcurrstatus == "selected"):
         selectnstatus = "joined / drop out";   
         Final_Status = "Yet to Process"


      cursor.execute("select count(*) as coun from candidate_stages where phoneno = %s", [Phoneno])
      count = cursor.fetchone()
      print(count[0])
      
      if (count[0] == 0):
         print("loop")
         cursor.execute("INSERT INTO candidate_stages (fname,lname,phoneno,i_date,curr_stage,new_stage,entered_date,updated_time,selected,rejected,final_status,competancy,location) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
         Fname,Lname,Phoneno,Idate,selectcstatus,selectnstatus,'NOW()','NOW()',rcurrstatus,rnewstatus,Final_Status,competancy,location
         ))         
         connection.commit()
         count = cursor.rowcount
      else:
         cursor.execute("INSERT INTO candidate_stages (fname,lname,phoneno,i_date,curr_stage,new_stage,updated_time,selected,rejected,final_status,competancy,location) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
         Fname,Lname,Phoneno,Idate,selectcstatus,selectnstatus,'NOW()',rcurrstatus,rnewstatus,Final_Status,competancy,location
         ))         
      
         connection.commit()
         count = cursor.rowcount


   else:
      print("ELSE CALLED")
      return "h"

@app.route('/search') 
def search_candidates():  
   return render_template('search_candidate.html') 

@app.route('/search_candidate_info',methods = ['POST', 'GET']) 
def search_info():  

   if request.method == 'POST':

      user_details = request.form['FirstName'];


      if( user_details.isdigit()):

         print("select count(*) from candidate_stages where phoneno= %s", [user_details])
         
         cursor.execute("select count(*) as coun from candidate_stages where phoneno = %s", [user_details])
         
         count = cursor.fetchone()
         

         if (count[0] > 0):

            cursor.execute("select max(id)  from candidate_stages where phoneno= %s", [user_details])
            maxid = cursor.fetchone();

            
            cursor.execute("select fname,lname,phoneno,curr_stage,new_stage,i_date  from candidate_stages where id= %s", [maxid[0]])
            mobile_records = cursor.fetchall();

            if(mobile_records):
               return render_template('search_candidate.html', name = mobile_records)
            else:
               return render_template('search_candidate.html', name = "NO RESULTS FOUND")

         else:
            
            print("PHONE NO ELSE PART")  
            cursor.execute("select fname,lname,phone_no,current_stage,new_stage,upload_time from fresh_candidate_upload where phone_no= %s", [user_details])
            mobile_records = cursor.fetchall() 

            if(mobile_records):
               return render_template('search_candidate.html', name = mobile_records)
            else:
               return render_template('search_candidate.html', name = "NO RESULTS FOUND")
            

      else:
         
         cursor.execute("select max(id)  from candidate_stages where phoneno= %s", [user_details])
         maxid = cursor.fetchone();

         cursor.execute("select count(*) from candidate_stages where fname = %s", [user_details])
         countofnames = cursor.fetchone();

         if(countofnames[0] > 0):

            cursor.execute("select max(id)  from candidate_stages where fname= %s", [user_details])
            maxid = cursor.fetchone();
            
            cursor.execute("select fname,lname,phoneno,curr_stage,new_stage,i_date  from candidate_stages where id  = %s", [maxid[0]])
            mobile_records = cursor.fetchall() 

            if(mobile_records):
               return render_template('search_candidate.html', name = mobile_records)
            else:
               return render_template('search_candidate.html', name = "NO RESULTS FOUND")   
            
         else:
           
            print("select fname,lname,phone_no,current_stage,new_stage,upload_time from fresh_candidate_upload where fname  = %s", [user_details])
            cursor.execute("select fname,lname,phone_no,current_stage,new_stage,upload_time from fresh_candidate_upload where fname  = %s", [user_details])
            mobile_records = cursor.fetchall() 
            print(mobile_records)

            if(mobile_records):
               return render_template('search_candidate.html', name = mobile_records)
            else:
               return render_template('search_candidate.html', name = "NO RESULTS FOUND")   

        
      

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      separateformat = f.filename.split('.');
      if separateformat[1] == "csv":
         print("THIS IS CSV FILE FORMAT")
         readanyotherformat(separateformat[0],separateformat[1])

      if separateformat[1] == "xls":
         print("THIS IS XLS FORMAT")
         readanyotherformat(separateformat[0],separateformat[1])

      if separateformat[1] == "XLSX" or separateformat[1] == "xlsx":
         print("THIS IS XLSX FORMAT") 
         insertion_count = readanyotherformat(separateformat[0],separateformat[1])

      print(insertion_count)
      if(insertion_count > 0):

         string_todisplay = "File Uploaded Succesfully";
         return render_template('file_upload.html',uploaded=string_todisplay)
      else:
         return "Please Upload the file"  
  
@app.route('/search_candidate', methods = ['GET', 'POST'])
def search_candidate():
   return render_template('search.html')

@app.route('/uploaded_report', methods = ['GET', 'POST'])
def upload_report():

   dept_name = request.args.get('deptname');

   print(dept_name)

   res2 = [];

   # cursor.execute("select fname,lname,phoneno, MIN(i_date) as idate,MIN(entered_date),MAX(updated_time) from candidate_stages group by phoneno,fname,lname")
   # mobile_records = cursor.fetchall()

   if(dept_name == "all"):
      cursor.execute("select fname,lname,phoneno,i_date,updated_time  from (select fname, lname,new_stage,phoneno,i_date,updated_time, row_number() over (partition by fname order by i_date desc) as r1 from candidate_stages)a where r1 =1")
      mobile_records = cursor.fetchall()
   else:
      cursor.execute("select fname,lname,phoneno,i_date,updated_time  from (select fname, lname,new_stage,phoneno,i_date,updated_time, row_number() over (partition by fname order by i_date desc) as r1 from candidate_stages)a where r1 =1 and new_stage= %s",[dept_name])
      mobile_records = cursor.fetchall()


   cursor.execute("select new_stage,count(r1) from (select new_stage, row_number() over (partition by fname order by i_date desc) as r1 from candidate_stages)a where r1 =1 group by 1")
   counts = cursor.fetchall()

   total_values = 0;
   for i in counts:
      total_values = total_values + i[1];

   print(total_values)   
      

   # res11 = [''.join(''.join(elems) for elems in mobile_records)];
   
   for row in mobile_records:
      
      res = cursor.execute("SELECT DATE_PART('day',%s::date) - DATE_PART('day',%s::date)",('NOW()',row[3]))
      diffsofor = cursor.fetchall()

      res1 = cursor.execute("SELECT DATE_PART('day',%s::date) - DATE_PART('day',%s::date)",('NOW()',row[4]))
      diffsoin = cursor.fetchall()

      res2.append([(row + tup1 + tup2) for tup1 in diffsofor for tup2 in diffsoin])
      
   return render_template('uploaded_report.html',data=res2,counts_ofdept=counts,total=total_values)
         
@app.route('/getcountdetails', methods = ['GET', 'POST'])
def count_details():


   dept_name = request.args.get('deptname');


   cursor.execute("select fname,lname,phoneno,i_date,updated_time  from (select fname, lname,new_stage,phoneno,i_date,updated_time, row_number() over (partition by fname order by i_date desc) as r1 from candidate_stages)a where r1 =1 and new_stage= %s",[dept_name])
   mobile_records = cursor.fetchall()

   return render_template('count_details.html',details=mobile_records)

  



   # return "hi"

if __name__ == '__main__':
   app.run(debug = True)