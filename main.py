
from unicodedata import category
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os
from sqlalchemy import func

app = Flask(__name__)

from configs.base_config import *
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:deno0707@localhost:5432/hotd'
app.config["SECRET_KEY"] = "#deno0707@mwangi"
# app.config.from_object(Development)


db = SQLAlchemy(app)

from models.Patient import Patient
from models.Staff import Staff
from models.Appointment import Appointment
from models.Role import Role
from models.charges import Charges
from models.visitors import Visitors
from models.inventory import Inventory
from utils.init_roles import *

# db.create_all()
@app.before_first_request
def create_tables():
    db.create_all()
    seeding()


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized! Please log in', 'danger')
            
            return redirect(url_for('login', next = request.url))
    return wrap




@app.route('/', methods = ['GET', 'POST'])
@login_required
def dashboard():
    logged_in = session['logged_in']
    first_name = session['first_name']
    last_name = session['last_name']

    patient_count = Patient.query.count()
    staff_count = Staff.query.count()
    doctor_count = Staff.query.filter_by(role = 2).count()
    appointment_count = Appointment.query.count()
    

    return render_template('dashboard.html', logged_in = logged_in, first_name = first_name, last_name = last_name, patient_count = patient_count, staff_count = staff_count, appointment_count = appointment_count, doctor_count = doctor_count)

@app.route('/patients', methods = ['GET', 'POST'])
@login_required
def patients():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        address = request.form['address']
        telephone = request.form['telephone_number']
        gname=request.form['gname']
        gtelephone_number=request.form['gtelephone_number']
        print(len(telephone))
        new_patient = Patient(first_name = first_name, last_name = last_name, gender = gender, address = address, telephone = telephone,guardian_name=gname,guardian_phone_no=gtelephone_number)

        db.session.add(new_patient)
        db.session.commit()

        flash("Patient successfully added", "success")

    logged_in = session['logged_in']
    first_name = session['first_name']
    last_name = session['last_name']

    genders = ['M', 'F']
    patients = Patient.query.all()
    doctors = Staff.query.all()

    return render_template('patients.html', genders = genders, patients = patients, doctors = doctors, logged_in = logged_in, first_name = first_name, last_name = last_name)

@app.route('/edit_patient', methods = ['POST'])
@login_required
def edit_patient():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        address = request.form['address']
        telephone = request.form['telephone']

        patient_to_edit = Patient.query.filter_by(id = patient_id).first()
        patient_to_edit.first_name = first_name
        patient_to_edit.last_name = last_name
        patient_to_edit.gender = gender
        patient_to_edit.address = address
        patient_to_edit.telephone = telephone

        db.session.add(patient_to_edit)
        db.session.commit()

        flash("Patient data successfully edited", "success")

        return redirect(url_for('patients'))

@app.route('/doctors', methods = ['GET', 'POST'])
@login_required
def doctors():        
    logged_in = session['logged_in']
    first_name = session['first_name']
    last_name = session['last_name']
    genders = ['M', 'F']
    roles = Role.query.all()
    medical_staff = Staff.query.all()
    print(medical_staff)

    return render_template('doctors.html',  medical_staff = medical_staff, roles = roles, logged_in = logged_in, first_name = first_name, last_name = last_name)

@app.route('/edit_doctor', methods = ['POST'])
@login_required
def edit_doctor():
    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        department = request.form['department']
        telephone = request.form['telephone']

        staff_to_edit = Staff.query.filter_by(id = doctor_id).first()
        staff_to_edit.first_name = first_name
        staff_to_edit.last_name = last_name
        staff_to_edit.department = department
        staff_to_edit.telephone = telephone

        db.session.add(staff_to_edit)
        db.session.commit()

        flash("Doctor data successfully edited", "success")

        return redirect(url_for('doctors'))

@app.route('/staff', methods = ['GET', 'POST'])
@login_required
def staff():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        department = request.form['department']
        role = request.form['role']
        telephone = request.form['telephone']
        email = request.form['email']
        password =  request.form['password']
        hashed_password = generate_password_hash(password = password)

        # check that email does not exist before registering the user
        if Staff.check_email_exists(email):
            flash("The user already exists. Please try registering with a different email.", "danger")
        else:
            new_staff_member = Staff(first_name = first_name, last_name = last_name, department = department, role = role, telephone = telephone, email = email, password = hashed_password)

            db.session.add(new_staff_member)
            db.session.commit()

            flash("Staff member successfully registered", "success")
        
    logged_in = session['logged_in']
    first_name = session['first_name']
    last_name = session['last_name']
    genders = ['M', 'F']
    staff = Staff.query.all()
    roles = Role.query.all()

    return render_template('staff.html', genders = genders, staff = staff, roles = roles, logged_in = logged_in, first_name = first_name, last_name = last_name)

@app.route('/edit_staff', methods = ['POST'])
@login_required
def edit_staff():
    if request.method == 'POST':
        staff_id = request.form['staff_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        department = request.form['department']
        role = request.form['role']
        telephone = request.form['telephone']
        
        staff_to_edit = Staff.query.filter_by(id = staff_id).first()
        staff_to_edit.first_name = first_name
        staff_to_edit.last_name = last_name
        staff_to_edit.department = department
        staff_to_edit.role = role
        staff_to_edit.telephone = telephone

        db.session.add(staff_to_edit)
        db.session.commit()

        flash("Staff data successfully edited", "success")

        return redirect(url_for('staff'))

@app.route('/dashboard_doc', methods = ['POST'])
@login_required
def dashboard_doc():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    department = "doctor"
    role = request.form['role']
    telephone = request.form['telephone']
    email = request.form['email']
    password =  '1234'
    hashed_password = generate_password_hash(password = password)

    # check that email does not exist before registering the user
    if Staff.check_email_exists(email):
        flash("The user already exists. Please try registering with a different email.", "danger")
    else:
        new_staff_member = Staff(first_name = first_name, last_name = last_name, department = department, role = role, telephone = telephone, email = email, password = hashed_password)

        db.session.add(new_staff_member)
        db.session.commit()

        flash("Doctor successfully registered", "success")

    return redirect(url_for('doctors'))

@app.route('/appointments', methods = ['GET', 'POST'])
@login_required
def appointments():
    if session:
        role = session['role']
        staff_id = session['staff_id']

        if request.method == 'POST':
            patient = request.form['patient']
            doctor = request.form['doctor']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            triage_report = request.form['triage_report']
            symptoms_report = request.form['symptoms_report']
            medication_report = request.form['medication_report']
            other_remarks = request.form['other_remarks']
            lab_report = request.form['lab_report']
            status = request.form['status']

            new_appointment = Appointment(patient = patient, doctor = doctor, start_time = start_time, end_time = end_time, triage_report = triage_report, symptoms_report = symptoms_report, medication_report = medication_report, other_remarks = other_remarks, lab_report = lab_report, status = status)

            db.session.add(new_appointment)
            db.session.commit()

            flash("Appointment successfully created", "success")

        logged_in = session['logged_in']
        first_name = session['first_name']
        last_name = session['last_name']

        patients = Patient.query.all()
        doctors = Staff.query.all()
        appointments = Appointment.query.all()

        return render_template('appointments.html', patients = patients, doctors = doctors, appointments = appointments, role = role, staff_id = staff_id, logged_in = logged_in, first_name = first_name, last_name = last_name)
    else:
        return redirect(url_for('login'))

@app.route('/edit_appointment', methods = ['POST'])
@login_required
def edit_appointment():
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']

        appointment_to_edit = Appointment.query.filter_by(id = appointment_id).first()
        
        patient = request.form.get('patient', appointment_to_edit.patient)
        doctor = request.form.get('doctor', appointment_to_edit.doctor)
        start_time = request.form.get('start_time', appointment_to_edit.start_time)
        end_time = request.form.get('end_time', appointment_to_edit.end_time)
        status = request.form.get('status', appointment_to_edit.status)
        triage_report = request.form.get('triage_report', appointment_to_edit.triage_report)
        symptoms_report = request.form.get('symptoms_report', appointment_to_edit.symptoms_report)
        medication_report = request.form.get('medication_report', appointment_to_edit.medication_report)
        other_remarks = request.form.get('other_remarks', appointment_to_edit.other_remarks)
        lab_report = request.form.get('lab_report', appointment_to_edit.lab_report)

        appointment_to_edit.patient = patient
        appointment_to_edit.doctor = doctor
        appointment_to_edit.start_time = start_time
        appointment_to_edit.end_time = end_time
        appointment_to_edit.status =status
        appointment_to_edit.triage_report = triage_report
        appointment_to_edit.symptoms_report = symptoms_report
        appointment_to_edit.medication_report = medication_report
        appointment_to_edit.other_remarks = other_remarks
        appointment_to_edit.lab_report = lab_report

        db.session.add(appointment_to_edit)
        db.session.commit()

        flash("Appointment data successfully edited", "success")

        return redirect(url_for('appointments'))

@app.route('/appointments/<int:x>', methods = ['GET'])
def patient_appointments(x):
    if request.method == 'GET':
        patient_appointments = Appointment.query.filter_by(patient = x).all()
        print(patient_appointments)

        logged_in = session['logged_in']
        first_name = session['first_name']
        last_name = session['last_name']

        return render_template('patient_appointments.html', appointments = patient_appointments, logged_in = logged_in, first_name = first_name, last_name = last_name)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        role = request.form['role']
        telephone = request.form['telephone']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password = password)
        department="surgeon"

        # check that email does not exist before registering the user
        if Staff.check_email_exists(email):
            flash("The user already exists. Please try registering with a different email.", "danger")
        else:
            new_staff_member = Staff(first_name = first_name, last_name = last_name, department = department, role = role, telephone = telephone, email = email, password = hashed_password)

            db.session.add(new_staff_member)
            db.session.commit()

            flash("You have successfully signed up. You can now log in to your account.", "success")

            return redirect(url_for('login'))

    genders = ['M', 'F']
    roles = Role.query.all()
 

    return render_template('register.html', genders = genders, roles = roles)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # check if email exist
        if Staff.check_email_exists(email = email):
           # if the email exists check if password is correct
           if Staff.check_password(email = email, password = password):
               session['logged_in'] = True
               session['first_name'] = Staff.fetch_by_email(email).first_name
               session['last_name'] = Staff.fetch_by_email(email).last_name
               session['role'] = Staff.fetch_by_email(email).roles.name
               session['staff_id'] = Staff.fetch_by_email(email).id

               return redirect(url_for('dashboard'))
           else:
               flash("Incorrect password","danger")

               return render_template('login.html')
        else:
            flash("Email does not exist","danger")

    return render_template("login.html")

# Log Out route
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out','success')

    return redirect(url_for('login'))

@app.route('/roles', methods = ['GET', 'POST'])
@login_required
def roles():
    if session:
        
        role = session['role']

        if request.method == 'POST':
            name = request.form['name']

            new_role = Role(name = name)

            db.session.add(new_role)
            db.session.commit()

            flash("Role successfully added", "success")
            
        logged_in = session['logged_in']
        first_name = session['first_name']
        last_name = session['last_name']
        
        roles = Role.query.all()

        return render_template('roles.html', roles = roles, role=role, logged_in = logged_in, first_name = first_name, last_name = last_name)
    else:
        return redirect(url_for("login"))

@app.route('/edit_role', methods = ['POST'])
@login_required
def edit_role():
    if request.method == 'POST':
        role_id = request.form['role_id']
        name = request.form['name']

        role_to_edit = Role.query.filter_by(id = role_id).first()
        role_to_edit.name = name

        db.session.add(role_to_edit)
        db.session.commit()

        flash("Role data successfully edited", "success")

        return redirect(url_for('roles'))
@app.route('/charges', methods = ['POST','GET'])
def charges():
    if request.method == 'POST':
        phone = request.form['phone']
        patient = Patient.query.filter_by(telephone=phone).first()
        if patient:
            session['chargesid']=patient.id
        
        
            return redirect(url_for("chargestable"))
        else:
            return render_template("telephoneform.html")
    else:
        return render_template("telephoneform.html")
@app.route('/bill', methods = ['POST','GET'])
def bill():
    if request.method == 'POST':
        service_offered=request.form['service_offered']
        cost = Inventory.query.filter_by(name=service_offered).first()
        cost= cost.selling_price
        x=session['chargesid']
        charges=Charges(patient_id=x,service_offered=service_offered,cost=cost)
        db.session.add(charges)
        db.session.commit()
        return redirect('/chargestable')
@app.route('/paybill', methods = ['POST','GET'])
def paybill():
    if request.method == 'POST':
        service_offered=request.form['service_offered']
        cost=request.form['cost']
        
        cost=int(cost)
        cost = -abs(cost)

        x=session['chargesid']
        charges=Charges(patient_id=x,service_offered=service_offered,cost=cost)
        db.session.add(charges)
        db.session.commit()
        return redirect('/chargestable')

@app.route('/chargestable', methods=['POST','GET'])
def chargestable():
    x=session['chargesid']
    charges=Charges.query.filter_by(patient_id=x).all()
    print(charges)
    total_cost=Charges.query.with_entities(func.sum(Charges.cost)).filter(Charges.patient_id==x).first()
    print(type(total_cost))
    total_cost=total_cost[0]
    inventory=Inventory.query.all()
    return render_template('charges.html',charges=charges,total_cost=total_cost,inventory=inventory)

    


@app.route('/visitor', methods=['POST','GET'])
def visitor():
    if request.method == 'POST':
            phone = request.form['phone']
            patient = Patient.query.filter_by(telephone=phone).first()
            session['pid']=patient.id
            
            return redirect(url_for("visitor_reg"))
    else:
        return render_template('patientsphoneform.html')

@app.route('/visitorsregistartion', methods=["POST","GET"]) 
def visitor_reg():
    if request.method=="POST":
        name=request.form["name"]
        pid=session['pid']
        phone=request.form["phone"]
        gender=request.form["gender"]
        visitor=Visitors(name=name,patient_id=pid,visitor_pnone=phone,gender=gender)
        db.session.add(visitor)
        db.session.commit()
        return redirect ('/visitorslist')
    else:
        genders = ['M', 'F']
        return render_template('visitorsregistrationform.html', genders=genders)

@app.route('/visitorslist', methods=["POST","GET"])
def visitors_list():
    visitors=Visitors.query.all()
    for visitor in visitors:
        print(visitor.patients.first_name)
    print(visitors)
    
    return render_template('visitorslist.html',visitors=visitors)

@app.route('/inventory',methods= ["POST","GET"])
def inventory():
    if request.method=="POST":
        name=request.form['name']
        category=request.form['category']
        selling_price=request.form['cost']
        new_product=Inventory(name=name,category=category,selling_price=selling_price)
        db.session.add(new_product)
        db.session.commit()
        return redirect('/inventory')
    else:
        inventory=Inventory.query.all()
        return render_template("inventory.html",inventory=inventory)

@app.route('/guardians',methods= ["POST","GET"])
def guardian():
    patients = Patient.query.all()
    return render_template("guardians.html",patients=patients)
    
        


    

if __name__ == '__main__':
    app.run(debug=True)