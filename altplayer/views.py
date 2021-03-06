import math

from flask import render_template
from flask import abort
from flask import request

from altplayer import app
from altplayer import db
from altplayer.iplayer import CATEGORIES

PAGE_SIZE = 20


@app.route('/programme/<pid>')
def view_programme(pid):
    programme = db.programmes.find_one({'pid': pid})

    if programme is not None:
        return render_template('programme.html', programme=programme)
    else:
        abort(404)

@app.route('/categories/<category>')
def view_category(category, episodes=False):
    if not episodes:
        order = request.args.get('order')
        if order is None:
            order = 'recent'
        elif order not in ('atoz', 'recent'):
            abort(404)
    else:
        order = 'atoz'

    page = request.args.get('page')
    if page is None:
        page = 1
    else:
        try:
            page = int(page)
        except ValueError:
            abort(404)

    if not episodes:
        programmes = db.programmes.find({'category': category})
    else:
        programmes = db.programmes.find({'episodes': category})

    programmes_count = programmes.count()

    if programmes_count == 0:
        abort(404)

    num_pages = int(math.ceil(programmes_count / float(PAGE_SIZE)))

    programmes = programmes.skip((page - 1) * PAGE_SIZE)
    programmes = programmes.limit(PAGE_SIZE)

    if order == 'atoz':
        if not episodes:
            programmes = programmes.sort('title', 1)
        else:
            programmes = programmes.sort('subtitle', 1)
    elif order == 'recent':
        programmes = programmes.sort('recency_rank', 1)

    programmes = list(programmes)

    episodes_count = {}

    if not episodes:
        for programme in programmes:
            if 'episodes' not in programme:
                continue
            find_document = {'episodes': programme['episodes']}
            episodes_cursor = db.programmes.find(find_document)
            episodes_count[programme['episodes']] = episodes_cursor.count()

    if not episodes:
        category_name = CATEGORIES[category]
    else:
        category_name = programmes[0]['title']

    return render_template('categories.html', programmes=programmes,
        num_pages=num_pages, category=category, page=page,
        category_name=category_name, episodes_count=episodes_count,
        episodes=episodes, order=order)

@app.route('/episodes/<episodes>')
def view_episodes(episodes):
    return view_category(episodes, episodes=True)

