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
def view_category(category):
    order = request.args.get('order')
    if order is None:
        order = 'recent'
    elif order not in ('atoz', 'recent'):
        abort(404)

    page = request.args.get('page')
    if page is None:
        page = 1
    else:
        try:
            page = int(page)
        except ValueError:
            abort(404)

    programmes = db.programmes.find({'category': category})
    programmes_count = programmes.count()

    if programmes_count == 0:
        abort(404)

    num_pages = int(math.ceil(programmes_count / float(PAGE_SIZE)))

    programmes = programmes.skip((page - 1) * PAGE_SIZE)
    programmes = programmes.limit(PAGE_SIZE)

    if order == 'atoz':
        programmes = programmes.sort('title', 1)
    elif order == 'recent':
        programmes = programmes.sort('recency_rank', 1)

    programmes = list(programmes)

    return render_template('categories.html', programmes=programmes,
        num_pages=num_pages, category=category, page=page,
        category_name=CATEGORIES[category])

