from flask import Flask, render_template, request, session
from checker import check_logged_in

from vsearch import search4letters
from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError

app = Flask(__name__)

app.config['dbconfig'] = { 'host': '127.0.0.1',
             'user': 'vsearch',
             'password': 'vsearchpasswd',
             'database': 'vsearchlogDB', }


@app.route('/login')
def do_login() -> str:
  session['logged_in'] = True
  return 'You are now logged in.'


@app.route('/logout')
def do_logout() -> str:
  session.pop('logged_in')
  return 'You are now logged out.'


@app.route('/')
def entry_page() -> 'html':
    return render_template('entry.html',
                            the_title="Welcome to search4letters on the Web!")


@app.route('/viewlog')
@check_logged_in
def view_log() -> 'html':
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """select phrase, letters, ip, browser_string, results
                    from log"""        
            cursor.execute(_SQL)
            contents = cursor.fetchall()
            titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')

            return render_template('viewlog.html',
                                    the_title='View Log',
                                    the_row_titles=titles,
                                    the_data=contents,)
    except ConnectionError as err:
        print('Is your database on? Error:', str(err))
    except CredentialsError as err:
        print('Username/password issue. Error:', str(err))
    except SQLError as err:
        print('SQL Query error:', str(err))
    except Exception as err:
        print('Something went wrong:', str(err))


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search4letters(phrase, letters))
    try:
        log_request(request, results)
    except Exception as err:
        print('***** Logging failed with this error:', str(err))
    return render_template('results.html',
                            the_title="Here are your results:",
                            the_phrase=phrase,
                            the_letters=letters,
                            the_results=results)


def log_request(req: 'flask_request', res: str) -> None:
    _SQL = """insert into log
              (phrase, letters, ip, browser_string, results)
              values
              (%s, %s, %s, %s, %s)"""
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            cursor.execute(_SQL, (req.form['phrase'],
                                req.form['letters'],
                                req.remote_addr,
                                req.user_agent.browser,
                                res, ))
    except ConnectionError as err:
        print('Is your database on? Error:', str(err))
    except CredentialsError as err:
        print('Username/password issue. Error:', str(err))
    except SQLError as err:
        print('SQL Query error:', str(err))
    except Exception as err:
        print('Something went wrong:', str(err))


app.secret_key = 'USE THIS TO SEED MY COOKIES, DAMNIT'
# don't call if module is imported (like a cloud provider) as they will call app.run()
if __name__ == '__main__':
    app.run(debug=True)
