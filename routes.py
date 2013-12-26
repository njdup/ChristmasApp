from sqlite3 import dbapi2 as sqlite3
from flask import Flask, render_template, request, session, g

app = Flask(__name__)

app.config.update(dict(
        DATABASE='/tmp/cards.db'))

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    print "initializing database"
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def home():
    db = get_db()
    cur = db.execute('select title from entries')
    entries = cur.fetchall()
#    for entry in entries:
 #       print entry.title
    return render_template('home.html', entries=entries)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/input')
def input():
    return render_template('enterInfo.html', error=None)

@app.route('/get_card/<title>')
def get_card(title):
    db = get_db()
    print title
#    if not title:
 #       return render_template('enterInfo.html',
  #                             error="No title given. Make a card to share!")
    lookup = 'select title, sender, recipient, message, background from entries where title=\'' + title + '\''
    print lookup
    cur = db.execute(lookup)
    print 'yes!'
    entries = cur.fetchall()
    if len(entries) != 1:
        return render_template('enterInfo.html',
                               error="Nonexistent title given. Make a card to share!")
    
    #    info = entry[0]
    for info in entries:
        print info
    return render_template('card.html', name=info[2], msg=info[3],
                           bg=info[4], sender=info[1], title=None)

    
@app.route('/input_response', methods=['GET', 'POST'])
def input_response():
    if request.method == 'POST':
        db = get_db()
        inputs = request.form.keys()
        if not 'background' in inputs: 
            return render_template('enterInfo.html',
                                   error="You must fill in all fields")
        title = request.form['title']
        recipient = request.form['recipient']
        sender = request.form['sender']
        message = request.form['message']
        background = request.form['background']
        if not recipient or not sender or not message or not title:
            return render_template('enterInfo.html',
                                   error="You must fill in all fields")
        
        lookup = 'select title from entries where title=\'' + title + '\''
        print lookup
        cur = db.execute(lookup)
        entries = cur.fetchall()
        if len(entries) > 0: 
            return render_template('enterInfo.html',
                                   error="That title has already been used.")
        
        db.execute('insert into entries (title, sender, recipient, message, background) values (?, ?, ?, ?, ?)', [title, sender, recipient, message, background])
        db.commit()
        return render_template('card.html', name=recipient,
                               msg=message, bg=background, sender=sender, title=title)
    
    elif request.method == 'GET':
        title = request.form['title']
        if not title:
            return render_template('enterInfo.html', 
                                   error="No title given. Make a card to share!")
        lookup = 'select title, sender, recipient, message, background from entries where title=\'' + title + '\''
        print lookup
        cur = db.execute(lookup)
        entries = cur.fetchall()
        if len(entries) != 1:
            return render_template('enterInfo.html',
                                   error="Nonexistent title given. Make a card to share!")
        
        info = entry[0]
        return render_template('card.html', name=info.recipient, msg=info.message,
                               bg=info.background, sender=info.sender, title=info.title)
    
        


if __name__ == '__main__':
    init_db()
    app.debug = True
    app.run()
