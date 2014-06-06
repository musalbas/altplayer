import re
import urllib2

from altplayer import db

CATEGORIES = {
    'arts': "Arts",
    'cbbc': "CBBC",
    'cbeebies': "CBeebies",
    'comedy': "Comedy",
    'documentaries': "Documentaries",
    'drama-and-soaps': "Drama & Soaps",
    'entertainment': "Entertainment",
    'films': "Films",
    'food': "Food",
    'history': "History",
    'music': "Music",
    'news': "News",
    'science-and-nature': "Science & Nature",
    'sport': "Sport",
    'audio-described': "Audio Described",
    'signed': "Signed",
    'northern-ireland': "Northern Ireland",
    'scotland': "Scotland",
    'wales': "Wales",
}

class _Sync:

    def __init__(self, programmes_collection, print_progress=False):
        self._programmes_collection = programmes_collection
        self._print_progress = print_progress

    def _parse_page_num_html(self, html):
        page_num_info = {}

        max_page_num = re.findall('>\d+<', html)
        max_page_num = int(max_page_num[-1][1:-1])
        page_num_info['max_page_num'] = max_page_num

        return page_num_info

    def _parse_programme_html(self, html):
        html_lines = html.split('\n')
        programme = {}

        programme['pid'] = re.search('/iplayer/episode/([a-z0-9]+)/',
            html_lines[0])
        programme['pid'] = programme['pid'].group(1)

        programme['title'] = re.search('<div class="title top-title">(.+)</div>',
            html_lines[0])
        programme['title'] = programme['title'].group(1)

        episodes = re.search('/iplayer/episodes/([a-z0-9]+)">',
            html_lines[1])
        if episodes is not None:
            programme['episodes'] = episodes.group(1)

        subtitle = re.search('<div class="subtitle"> (.*) </div>   <p',
            html_lines[1])
        if subtitle is not None:
            programme['subtitle'] = subtitle.group(1)

        programme['synopsis'] = re.search('<p class="synopsis"> (.*) </p> <p>',
            html_lines[1])
        programme['synopsis'] = programme['synopsis'].group(1)

        availability = re.search('<span class="availability"> (.*) left',
            html_lines[1])
        if availability is not None:
            programme['availability'] = availability.group(1)

        programme['duration'] = re.search('(\d+) mins', html_lines[1])
        programme['duration'] = programme['duration'].group(1)

        brand = re.search('<span class="medium">([^<]+)',
            html_lines[1])
        if brand is not None:
            programme['brand'] = brand.group(1)

        return programme

    def _print(self, output):
        if self._print_progress:
            print(output)

    def _pull_category_page(self, category_id, page_num, episodes=False):
        if not episodes:
            url = ("http://www.bbc.co.uk/iplayer/categories/" + category_id
                + "/all?sort=dateavailable&page=" + str(page_num))
        else:
            url = ("http://www.bbc.co.uk/iplayer/episodes/" + category_id
                + "?page=" + str(page_num))

        data = urllib2.urlopen(url).read()

        page = {}
        page['programmes'] = []

        programme_counter = 0
        prev_programme_line = ''
        for line in data.split('\n'):

            if ('<div class="play-icon">' in line
                or '<div id="blq-content"' in line):

                if prev_programme_line == '':
                    prev_programme_line = line
                    continue

                programme_counter += 1

                if episodes and programme_counter < 2:
                    continue

                programme = self._parse_programme_html(prev_programme_line
                    + '\n' + line)
                
                if not episodes:
                    programme['recency_rank'] = (page_num * 100
                        + programme_counter)

                if not episodes:
                    programme['category'] = category_id
                else:
                    programme['episodes'] = category_id

                page['programmes'].append(programme)

                self._print(
                    ("  " if episodes else "")
                    + category_id + "/"
                    + str(page_num) + "/"
                    + str(programme_counter) + "/"
                    + programme['title'] + "/"
                    + (programme['subtitle'] if 'subtitle' in programme else "")
                )

                prev_programme_line = line

            if '<li class="page focus">' in line:
                page_num_info = self._parse_page_num_html(line)
                page['max_page_num'] = page_num_info['max_page_num']

        if 'max_page_num' not in page:
            page['max_page_num'] = 1

        return page

    def _sync_category(self, category_id, episodes=False):
        page_counter = 1
        programmes = []
        while True:
            page = self._pull_category_page(category_id, page_counter,
                episodes)
            for programme in page['programmes']:
                if not episodes and 'episodes' in programme:
                    programmes.append(
                        self._sync_category(programme['episodes'],
                            episodes=True)
                    )
                pid = programme['pid']
                self._programmes_collection.update({'pid': pid}, programme,
                    upsert=True)
                programmes.append(programme)
            if page['max_page_num'] == page_counter:
                break
            page_counter += 1

        return programmes

    def run(self):
        programmes_count = 0
        for category_id in CATEGORIES:
            programmes_count += len(self._sync_category(category_id))
        self._print("")
        self._print("Found " + str(programmes_count) + " programmes.")


def run_sync(print_progress=False):
    _Sync(db.programmes_tmp, print_progress=print_progress).run()
    
    db.programmes.drop()
    db.programmes_tmp.rename('programmes')

    if print_progress:
        print("Programmes collection updated.")
