from flask import Flask, render_template, request, json, session, redirect
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from functools import wraps
from model import ConsumerExtension as consumer_extension

from flask_restful import Resource, Api
from flask_restful import reqparse


app = Flask(__name__)
app.debug = True
mysql = MySQL()
app.secret_key = 'why would I tell you my secret key?'
api = Api(app)



# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1941233'
app.config['MYSQL_DATABASE_DB'] = 'Consumer'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

class AddHost(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('hostname', type=str)
            parser.add_argument('dc', type=str)
            args = parser.parse_args()

            _hostname = args['hostname']
            _dc = args['dc']

            # print _hostname, _dc

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_CreateNewHost',(_hostname,_dc))
            data = cursor.fetchall()

            conn.commit()
            return {'StatusCode':'200','Message': 'Success'}

        except Exception as e:
            return {'API error': str(e)}

class GetHosts(Resource):
    def post(self):
        try:
            # Parse the arguments
            # parser = reqparse.RequestParser()
            # parser.add_argument('hostname', type=str)
            # parser.add_argument('dc', type=str)
            # args = parser.parse_args()

            # _hostname = args['hostname']
            # _dc = args['dc']

            # print _hostname, _dc

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_CreateNewHost',(_hostname,_dc))
            data = cursor.fetchall()

            conn.commit()
            return {'StatusCode':'200','Message': 'Success'}

        except Exception as e:
            return {'API error': str(e)}

class UpdateHost(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('hostname', type=str)
            parser.add_argument('dc', type=str)
            args = parser.parse_args()

            _hostname = args['hostname']
            _dc = args['dc']

            # print _hostname, _dc

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_CreateNewHost',(_hostname,_dc))
            data = cursor.fetchall()

            conn.commit()
            return {'StatusCode':'200','Message': 'Success'}

        except Exception as e:
            return {'API error': str(e)}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            return redirect('/showSignin')
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def main():
    return redirect('/userHome')
    # if session.get('user'):
    #     return redirect('/userHome')
    # else:
    #     return redirect('/showSignin')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    return render_template('login.html')


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin', (_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]), _password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html', error='Wrong Email address or Password.')
        else:
            return render_template('error.html', error='Wrong Email address or Password.')


    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/userHome')
@login_required
def userHome():
    # if session.get('user'):
    hosts_dict = {}
    con = mysql.connect()
    cursor = con.cursor()
    cursor.execute("Select * from tbl_hosts")
    hosts = cursor.fetchall()
    cursor.execute("Select * from tbl_failed_hosts")
    failed_hosts = cursor.fetchall()
        #
        # for host in hosts:
        #     hosts_dict.update({"hostname:": host[1], "dc": host[2], "created_date": host[3]})

    return render_template('index.html', all_hosts = hosts, failed_hosts = failed_hosts)
    # else:
    #     return render_template('error.html', error='Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/showSignin')

@app.route('/signUp', methods=['POST'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:

            # All Good, let's call MySQL

            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser', (_name, _email, _hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message': 'User created successfully !'})
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


api.add_resource(AddHost, '/AddHost')

if __name__ == "__main__":
    app.run()