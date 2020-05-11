from flask import Flask, render_template, request
from vsearch import search4letters

app = Flask(__name__)


@app.route('/')
def entry_page() -> 'html':
    return render_template('entry.html',
                            the_title="Welcome to search4letters on the Web!")


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search4letters(phrase, letters))

    return render_template('results.html',
                            the_title="Here are your results:",
                            the_phrase=phrase,
                            the_letters=letters,
                            the_results=results)


# don't call if module is imported (like a cloud provider) as they will call app.run()
if __name__ == '__main__':
    app.run(debug=True)
