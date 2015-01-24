import traceback
import os
import psycopg2
import urlparse
from flask import Flask, Response, request
from datetime import *

def get_connection():
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

    return conn

app = Flask(__name__)

@app.route("/")
def hello():
    html = 'gwyb - Hello world!!'
    return Response(html, mimetype='text/html')

@app.route('/book', methods=['POST'])
def book_appointment():
    try:
        doc = lxml.etree.fromstring(request.stream.read())

        uuid            = xfirst(doc.xpath('/data/@instance-id'))

        first_name      = xfirst(doc.xpath('/data/Patient/FirstName/text()'))
        last_name       = xfirst(doc.xpath('/data/Patient/LastName/text()'))
        nhs_number      = xfirst(doc.xpath('/data/Patient/NHSNumber/text()'))
        date_of_birth   = xfirst(doc.xpath('/data/Patient/Dob/text()'))
        tel_no          = xfirst(doc.xpath('/data/Patient/ContactTel/text()'))
        urgency         = ''

        allergies           = xfirst(doc.xpath('/data/ReferralDetails/Allergies/text()'))
        medical_history     = xfirst(doc.xpath('/data/ReferralDetails/MedicalHistory/text()'))
        
        bleeding_disorders  = xfirst(doc.xpath('/data/ReferralDetails/BleedingDisorders/text()'))
        medications         = xfirst(doc.xpath('/data/ReferralDetails/Medications/text()'))
        treatment_requested = xfirst(doc.xpath('/data/ReferralDetails/TreatmentRequested/text()'))
        parents_aware_flag  = xfirst(doc.xpath('/data/ReferralDetails/ParentsAware/text()'))

        problem_teeth = ''
        pt_ul               = xfirst(doc.xpath('/data/ReferralDetails/ProblemTeeth/UpperLeft/text()'))
        pt_ur               = xfirst(doc.xpath('/data/ReferralDetails/ProblemTeeth/UpperRight/text()'))
        pt_ll               = xfirst(doc.xpath('/data/ReferralDetails/ProblemTeeth/LowerLeft/text()'))
        pt_lr               = xfirst(doc.xpath('/data/ReferralDetails/ProblemTeeth/LowerRight/text()'))

        if pt_ul != '':
            problem_teeth += 'Upper-left: ' + pt_ul + "\n"
        if pt_ur != '':
            problem_teeth += 'Upper-right: ' + pt_ur + "\n"
        if pt_ll != '':
            problem_teeth += 'Lower-left: ' + pt_ll + "\n"
        if pt_lr != '':
            problem_teeth += 'Lower-right: ' + pt_lr + "\n"



        appointment_date, time_of_day    = doc.xpath('/data/Appointment/ApptDate/text()')[0].split()
    except Exception, err:
        print "Error parsing XML"
        print traceback.format_exc()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                  INSERT INTO patients
                  (first_name, last_name, nhs_number, date_of_birth, tel_no, urgency)
                  VALUES
                  (%s, %s, %s, %s, %s, %s)
			      RETURNING id
                """
                values = (first_name, last_name, nhs_number, date_of_birth, tel_no, urgency)
                cur.execute(query, values)
                patient_id = cur.fetchone()[0]		
                print "patient_id is %s\n" , patient_id
    except Exception, err:
        print "Error writing patient"
        print traceback.format_exc()


    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                  INSERT INTO referrals
                  (patient_id, uuid, allergies, medical_history, bleeding_disorders, medications, treatment_requested, parents_aware_flag, problem_teeth, referral_date)
                  VALUES
                  (%s, %s, %s, %s, %s, %s, %s, %s, %s, now())
                """
                values = (patient_id, uuid, allergies, medical_history, bleeding_disorders, medications, treatment_requested, parents_aware_flag, problem_teeth)
                cur.execute(query, values)
    except Exception, err:
        print "Error writing referral"
        print traceback.format_exc()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                  INSERT INTO appointments
                  (patient_id, appointment_date, time_of_day)
                  VALUES
                  (%s, %s, %s)
                """
                values = (patient_id, appointment_date, time_of_day)
                cur.execute(query, values)
    except Exception, err:
        print "Error writing referral"
        print traceback.format_exc()
    return "OK"

@app.route("/appointments")
def get_appointments():
    try:
        today = datetime.today()
        print today.strftime("%U")

    
        weeknum = datetime.date(today).isocalendar()[1]

    except Exception, err:
        print "Error processing dates"
        print traceback.format_exc()
    



    xml = """
       <AppointmentList>
         <Appointment>
           <ApptDate>01-Oct-2014 (AM)</ApptDate>
         </Appointment>
         <Appointment>
           <ApptDate>01-Oct-2014 (PM)</ApptDate>
         </Appointment>
         <Appointment>
           <ApptDate>08-Oct-2014 (AM)</ApptDate>
         </Appointment>
         <Appointment>
           <ApptDate>08-Oct-2014 (PM)</ApptDate>
         </Appointment>
       </AppointmentList>
    """

    return Response(xml, mimetype='text/xml')

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT to_char(appointment_date, 'DD-Mon-YYYY') as appointment_date, time_of_day, count(*) 
                                FROM appointments
                                WHERE appointment_date >= now()
                                AND appointment_date <= now() + interval '3 months' 
                                GROUP BY to_char(appointment_date, 'DD-Mon-YYYY'), time_of_day
                                HAVING count(*) < 4
                        """)
                xml = '<AppointmentList>'
                #for x in cur.fetchall():
                #    result += x.appointment_date
                rows = cur.fetchall()
                for row in rows:
                    xml += "<Appointment>\n<ApptDate>" + row[0] + " " + row[1] + "</ApptDate></Appointment>"
                xml += '</AppointmentList>'
                    
    except Exception, err:
        print "Error reading DB"
        print traceback.format_exc()
    return Response(xml, mimetype='text/xml')

def xstr(s):
    print s
    return '' if s is None else str(s)

def xfirst(s):
    if s:
        return s[0] 
    return ''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
