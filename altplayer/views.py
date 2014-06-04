from flask import render_template

from altplayer import app
from altplayer import iplayer
from altplayer import programmes

@app.route('/programme/<pid>')
def view_programme(pid):
    return render_template('programme.html', programme=programmes[pid])
