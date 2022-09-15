from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql.cursors
import smtplib
from email.mime.text import MIMEText
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from UserLogin import UserLogin

app = Flask(__name__)
app.config['SECRET_KEY'] = '********'

login_manager = LoginManager(app)
login_manager.login_view = 'entrance_form'
login_manager.login_message = 'you need to login'
login_manager.login_message_category = 'success'


@login_manager.user_loader
def user_loader(user_id):
    return UserLogin(user_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/write', methods=['POST', 'GET'])
def write():
    text = request.form['inputText']
    try:
        connection = pymysql.connect(
            host='eu-cdbr-west-03.cleardb.net',
            user='b323bcd6eb6f22',
            password='********',
            database='heroku_ed4c340f60593cf',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            sql = "INSERT INTO `new_table` (`info`) VALUES ('%s')" % text
            cursor.execute(sql)
            connection.commit()

        connection.close()
    except Exception as ex:
        return 'exception'
    return text


@app.route('/view')
@login_required
def view():
    try:
        connection = pymysql.connect(
            host='eu-cdbr-west-03.cleardb.net',
            user='b323bcd6eb6f22',
            password='********',
            database='heroku_ed4c340f60593cf',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            sql = 'SELECT * FROM new_table'
            cursor.execute(sql)
            rows = cursor.fetchall()

        connection.close()
    except Exception as ex:
        return 'exception'

    result = []
    for row in rows:
        result.append([row['id'], row['info']])
        print(row)
    return result


@app.route('/email')
def send_email():
    send_from = '**********@gmail.com'
    password = '***************'
    send_to = '***********@icloud.com'

    message = 'message from python'
    msg = MIMEText(message)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    try:
        server.login(send_from, password)
        server.sendmail(send_from, send_to, f'Subject: INTERESTING EMAIL\n{msg.as_string()}')
        return 'message was sent'
    except Exception as ex:
        print(ex)
        return 'something go wrong'


@app.route('/entrance_form')
def entrance_form():
    if current_user.is_authenticated:
        return redirect(url_for('view'))
    return render_template('entrance.html')


@app.route('/registration_form')
def registration_form():
    return render_template('registration.html')


@app.route('/cabinet_reg', methods=['POST', 'GET'])
def cabinet():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    repeat_password = request.form['repeat_password']
    if password != repeat_password:
        return 'passwords must be similar'

    try:
        connection = pymysql.connect(
            host='eu-cdbr-west-03.cleardb.net',
            user='b323bcd6eb6f22',
            password='********',
            database='heroku_ed4c340f60593cf',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            sql = f'SELECT COUNT(email) FROM users WHERE email LIKE "{email}"'
            cursor.execute(sql)
            is_registered = cursor.fetchall()[0]['COUNT(email)']
            if is_registered != 0:
                return 'This email already registered'

        with connection.cursor() as cursor:
            sql = f'INSERT INTO users (username, email, password) VALUES ("{username}", "{email}", "{password}")'
            cursor.execute(sql)
            connection.commit()

        connection.close()
    except Exception as ex:
        print(ex)
        return 'database not available'

    return 'Registration is successful'


@app.route('/cabinet_enter', methods=['POST', 'GET'])
def cabinet_enter():
    email = request.form['email']
    password = request.form['password']
    try:
        connection = pymysql.connect(
            host='eu-cdbr-west-03.cleardb.net',
            user='b323bcd6eb6f22',
            password='********',
            database='heroku_ed4c340f60593cf',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            sql = f'SELECT * FROM users WHERE email LIKE "{email}"'
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result)
            if result['password'] == password:
                user = UserLogin(result['id'])
                login_user(user)
                return redirect(url_for('view'))
            else:
                return 'wrong password'

    except Exception as ex:
        print(ex)
        return 'database not available'


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    flash('you logout')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
