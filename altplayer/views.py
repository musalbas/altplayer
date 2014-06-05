from flask import render_template

from altplayer import app


@app.route('/programme/<pid>')
def view_programme(pid):
    pass
