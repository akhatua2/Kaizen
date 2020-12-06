from flask import Flask, render_template, request, jsonify, redirect, url_for
import pyrebase
import uuid
import requests
import datetime
#from werkzeug import secure_filename

app = Flask(__name__)

NLP_KEY = "AIzaSyBQAx6N94BhHUsDsquadh2zzUGNiBXdhGA"
SENT_ANALYSIS_URL = "https://language.googleapis.com/v1/documents:analyzeSentiment"

config = {
  "apiKey": "AIzaSyBG0wTnjzB9vbK1TvJiPPzpZ4vqevlOVDs",
  "authDomain": "hackduke-dd652.firebaseapp.com",
  "databaseURL": "https://hackduke-dd652-default-rtdb.firebaseio.com/",
  "storageBucket": "hackduke-dd652.appspot.com"
}

firebase = pyrebase.initialize_app(config)
DB_REF = firebase.database()



def score(sentence):
    url = SENT_ANALYSIS_URL
    data = {"document": {"content": sentence, "type": "PLAIN_TEXT"}}
    params = {"key": NLP_KEY}
    r = requests.post(url, params=params, json=data)
    magnitude = r.json()['documentSentiment']['magnitude']
    score = r.json()['documentSentiment']['score']
    if score >= 0:
        score = (score * 5 + 5) + magnitude
    else:
        score = (score * 5 + 5) - magnitude
    if score > 10:
        score = 10
    elif score < 0:
        score = 0
    return round(score,5)
    # return score

@app.route('/')
def patient_splash():
    # print(JOURNAL_ENTRIES_REF.child("blah").get().val()["content"])
    return render_template("patient.html")

@app.route('/myjournal')
def my_journal():
    entries = DB_REF.get().val()
    if entries is not None:
        entries = [entry_tuple[1] for entry_tuple in entries.items()][::-1]
    # more sauce
    return render_template("journal.html", entries=entries)

@app.route('/doctors/patients')
def patients():
    return render_template("patients.html")

@app.route('/doctors')
def doctor_splash(): 
    entries = DB_REF.get().val()
    if entries is not None:
        entries = [entry_tuple[1] for entry_tuple in entries.items()][::-1]
        scores =  [entry["score"] for entry in entries]
        score_avg = sum(scores)/float(len(scores))
        score_type_dist = [{"type":"Concern","count":0}, {"type":"Moderate","count":0}, {"type":"Good","count":0}]
        for score in scores:
            if score < 3.5:
                score_type_dist[0]["count"] += 1
            elif score < 6.5:
                score_type_dist[1]["count"] += 1
            else:
                score_type_dist[2]["count"] += 1
        return render_template("doctor.html", entries=entries, 
                            scores=scores, score_avg=score_avg, 
                            score_type_dist=score_type_dist)
    
    return render_template("doctor.html")

@app.route('/write', methods=['POST'])
def submit_journal_entry():
    if request.method == 'POST':
        if 'entry' in request.form:
            entry = request.form['entry']
            rating = score(entry)
        
            data = {
                    "date": str(dateme.datetime.now()), 
                    "content": entry, 
                    "score": rating
                    }
            DB_REF.push(data)
    return redirect((url_for('patient_splash')))
