import traceback
import json
import os
import psycopg2
import psycopg2.extras
import urlparse
from flask import Flask, Response, request, render_template
from datetime import *
import smtplib
import sendgrid

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart




app = Flask(__name__)

from flask.ext.cors import CORS, cross_origin
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'



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


@app.route("/")
def hello():
    html = 'gwyb - Hello world!!'
    return Response(html, mimetype='text/html')


@cross_origin()
@app.route('/rules', methods=['GET'])
def get_rules():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:


                query = """
                  SELECT * FROM rules
                """
                query = """ 
                    SELECT nhs_number, event_code, action_code, email, tel_no, payload 
                    FROM rules, actions 
                    where rules.id = actions.rule_id
                """
                cur.execute(query)

                json_names = ['nhsid', 'at', 'type', 'address', 'number', 'text']
                records = []

                #for rec in cur.fetchone():
                for rec in cur:
                    json_rec = {}
                    for i in range(6):
                        if json_names[i] is not None:
                            json_rec[json_names[i]] = rec[i]     
    
                    records.append(json_rec)

                return json.dumps(records)
                #return render_template("patients.html", records=records, title = 'Projects')
    except Exception, err:
        print "Error reading rules"
        print traceback.format_exc()


def send_email_heroku (subject, sender, recipient, content):
    # using SendGrid's Python Library - https://github.com/sendgrid/sendgrid-python

    api_key = '4c497bdc-8eab-43eb-b492-ca70f2941af6'
    api_user = 'is9999@gmail.com'

    sg = sendgrid.SendGridClient(api_user, api_key)
    message = sendgrid.Mail()

    message.add_to(recipient)
    message.set_from(sender)
    message.set_subject(subject)
    message.set_html(content)

    sg.send(message)

def send_email(subject, sender, recipient, content):
    return
    msg = MIMEMultipart()

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    text = MIMEText(content)

    msg.attach(text)

    s = smtplib.SMTP('localhost')
    s.sendmail(sender, [recipient], msg.as_string())
    s.quit()

@cross_origin()
@app.route('/trigger', methods=['GET'])
def event():
    send_email_heroku('A subject', 'jhgaw@kjkhawd.qwe', 'is9999@gmail.com', 'SOme content from heroku')
    return 'OK'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
