from flask import render_template
from flask import abort

from altplayer import app
from altplayer import db


@app.route('/programme/<pid>')
def view_programme(pid):
    programme = db.programmes.find_one({'pid': pid})

    if programme is not None:
        return render_template('programme.html', programme=programme)
    else:
        abort(404)
