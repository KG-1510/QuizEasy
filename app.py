import os
import sqlite3
from flask import Flask, flash, render_template, redirect, session, url_for, g
from flask.globals import request
from werkzeug.utils import secure_filename
from workers import pdf2text, txt2questions

# Constants
UPLOAD_FOLDER = './pdf/'
currentLocation = os.path.dirname(os.path.abspath(__file__))
questionLength = 0
correctAnswers = []



# Init an app object
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'TeamQuizEasy'

@ app.errorhandler(404)
def invalid_route(e):
    """ The page rendered when incorrect URL is typed """
    return render_template('404.html')

@ app.route('/')
def index():
    """ The landing page for the app from scratch """
    return render_template('index.html')

@ app.route('/upload')
def upload():
    if g.user:
        return render_template('upload.html')
    return render_template('unauthorized.html')

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']
 
@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return redirect('/')

@ app.route('/signin')
def signin():
    return render_template('signin.html')

@ app.route('/signin', methods=['POST'])
def checklogin():
    UN = request.form['Username']
    PW = request.form['Password']

    sqlconnection = sqlite3.Connection(currentLocation+"\\Login.db")
    cursor = sqlconnection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Users(Username text, Password text);")
    sqlconnection.commit()
    query1 = "SELECT Username, Password from Users WHERE Username = '{un}' AND Password = '{pw}'".format(un = UN, pw = PW)

    rows = cursor.execute(query1)
    rows = rows.fetchall()
    if len(rows) == 1:
        if request.method == 'POST':
            session.pop('user', None)
            
            if request.form['Password'] == PW:
                session['user'] = request.form['Username']
                return redirect('/upload')


    else:
        flash("❌ Invalid credentials! Try again or sign up!")
    return render_template('signin.html')


@ app.route('/signup', methods=['GET','POST'])
def registerpage():
    if request.method == "POST":
        dUN = request.form['DUsername']
        dPW = request.form['DPassword']
        cPW = request.form['confPw']
        sqlconnection = sqlite3.Connection(currentLocation+"\\Login.db")
        cursor = sqlconnection.cursor()
        try:
            if cPW == dPW:
                checkUser = "SELECT Username, Password from Users WHERE Username = '{dun}' AND Password = '{dpw}'".format(dun = dUN, dpw = dPW)
                rows = cursor.execute(checkUser)
                rows = rows.fetchall()
                if len(rows) == 1:
                    flash("❗ User already exists, try logging in!")
                else:
                    query1 = "INSERT INTO Users VALUES('{u}','{p}')".format(u = dUN, p = dPW)
                    cursor.execute(query1)
                    sqlconnection.commit()
                    flash("🎉 Awesome! Account created, now log in to your account!")
                    return redirect('/signin')
            else:
                flash("🤨 Password and Confirm password don't match, try again!")
                return render_template('signup.html')
        except:
            flash("⛔ Unknown error occured, try again later!")
            return render_template('signup.html')
    return render_template('signup.html')

@ app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """ Handle upload and conversion of file + other stuff """

    UPLOAD_STATUS = False
    questions = dict()

    # Make directory to store uploaded files, if not exists
    if not os.path.isdir('./pdf'):
        os.mkdir('./pdf')

    if request.method == 'POST':
        try:
            # Retrieve file from request
            uploaded_file = request.files['file']
            file_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                secure_filename(
                    uploaded_file.filename))
            file_exten = uploaded_file.filename.rsplit('.', 1)[1].lower()

            # Save uploaded file
            uploaded_file.save(file_path)
            # Get contents of file
            uploaded_content = pdf2text(file_path, file_exten)
            questions = txt2questions(uploaded_content)

            # Store the length of questions dict in global var
            global questionLength
            questionLength = len(questions)

            # Store correct answers in global var
            global correctAnswers

            for i in range(questionLength):
                correctAnswers.append(questions[i+1]['answer'])

            # File upload + convert success
            if uploaded_content is not None:
                UPLOAD_STATUS = True
        except Exception as e:
            print(e)
    return render_template(
        'quiz.html',
        uploaded=UPLOAD_STATUS,
        questions=questions,
        size=len(questions))


@app.route('/result', methods=['POST', 'GET'])
def result():
    if g.user:
        correct_q = 0
        selectedOptions = [] 
        for i in range(questionLength):
            radioGroupName = 'question'+str(i+1)
            option = request.form.getlist(radioGroupName)
            selectedOptions.append(option[0])
        for i in selectedOptions:
            for k in correctAnswers:
                if(i == k):
                    correct_q += 1    
        return render_template('result.html', total=5, correct=correct_q)
    return render_template('unauthorized.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
