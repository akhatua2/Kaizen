from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def patient_splash():
    return render_template("patient.html")

@app.route('/doctors')
def doctor_splash():
    return render_template("doctor.html")

@app.route('/write', methods=['POST'])
def submit_journal_entry():
