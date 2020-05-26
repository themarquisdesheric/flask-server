from flask import Flask, render_template, request, escape
from vsearch import search4letters
from DBcm import UseDatabase

app = Flask(__name__)

app.config['dbconfig'] = { 'host': '127.0.0.1',
             'user': 'vsearch',
             'password': 'vsearchpasswd',
             'database': 'vsearchlogDB', }


@app.route('/')
def entry_page() -> 'html':
    return render_template('entry.html',
                            the_title="Welcome to search4letters on the Web!")


@app.route('/viewlog')
def view_log() -> 'html':
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


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search4letters(phrase, letters))

    log_request(request, results)

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

    with UseDatabase(app.config['dbconfig']) as cursor:
        cursor.execute(_SQL, (req.form['phrase'],
                              req.form['letters'],
                              req.remote_addr,
                              req.user_agent.browser,
                              res, ))


# don't call if module is imported (like a cloud provider) as they will call app.run()
if __name__ == '__main__':
    app.run(debug=True)
