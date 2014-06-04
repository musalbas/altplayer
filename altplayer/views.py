from altplayer import app
from altplayer import iplayer
from altplayer import programmes

@app.route('/programme/<pid>')
def view_programme(pid):
    return str(programmes[pid])
