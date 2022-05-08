from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/getemp", methods=['GET', 'POST'])
def getemp():
    return render_template('GetEmp.html')


@app.route("/editemp", methods=['GET', 'POST'])
def editemp():
    return render_template('EditEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


@app.route("/fetchdata", methods=['POST'])
def GetEmp():    
    fetch_sql = "select * from employee"
    cursor = db_conn.cursor()
    
    try:
        cursor.execute(fetch_sql)
        allemp = cursor.fetchall()
        db_conn.commit()
    
    finally:
        cursor.close()
        
    return render_template('GetEmpOutput.html', allemp = allemp)


@app.route("/editEmp", methods=['POST'])
def editEmp():
    connection = create_connection()
    employeeId = request.form['employeeId']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    gender = request.form['gender']
    dateOfBirth = request.form['dateOfBirth']
    identityCardNumber = request.form['identityCardNumber']
    email = request.form['email']
    mobile = request.form['mobile']
    address = request.form['address']
    salary = request.form['salary']
    department = request.form['department']
    hireDate = request.form['hireDate']
    currentEmployeeId = request.form['currentEmployeeId']

    emp_image_file = request.files['image']
    split_tup = os.path.splitext(emp_image_file.filename)
    file_extension = split_tup[1]
   

    if emp_image_file.filename == "":
        updateEmployeeSql = "UPDATE employee set id= %s,first_name= %s,last_name= %s,gender= %s,date_of_birth= %s,identity_card_number= %s,email= %s,mobile= %s,address= %s,salary= %s,department= %s,hire_date= %s WHERE id=%s"
        cursor = connection.cursor()
        
        try:
            cursor.execute(updateEmployeeSql, (employeeId, firstName, lastName, gender, dateOfBirth,identityCardNumber, email, mobile, address, salary, department, hireDate,currentEmployeeId))
            emp_name = "" + firstName + " " + lastName
            db_conn.commit()
        finally:
            connection.close()
        return render_template('GetEmpOutput.html', name=emp_name, employeeId=employeeId)

    else:
        updateEmployeeSql = "UPDATE employee set id= %s,first_name= %s,last_name= %s,gender= %s,date_of_birth= %s,identity_card_number= %s,email= %s,mobile= %s,address= %s,salary= %s,department= %s,image= %s,hire_date= %s WHERE id=%s"
        cursor = connection.cursor()


    try:
        cursor.execute(updateEmployeeSql, (employeeId, firstName, lastName, gender, dateOfBirth, 
        identityCardNumber, email, mobile, address, salary, department, emp_image_file, hireDate,currentEmployeeId))
        cursor.execute(insert_sql)
        db_conn.commit()
        emp_name = "" + firstName + " " + lastName
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(employeeId) + "_image_file"+ file_extension
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)
            update_sql = "UPDATE employee set image = %s WHERE id=%s"
            cursor = connection.cursor()
            cursor.execute(update_sql, (object_url,employeeId))
            db_conn.commit()


        except Exception as e:
            print("running expection")
            print(e)
            return str(e)

    finally:
        print("running finally")
        
        connection.close()

    print("all modification done...")
    return render_template('GetEmpOutput.html', name=emp_name, employeeId=employeeId)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
