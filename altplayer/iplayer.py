import json
import urllib2

class Programmes:

    def __init__(self, programmes_db):
        self._programmes_db = programmes_db

    def __getitem__(self, pid):
        programme = self._programmes_db.find_one({'pid': pid})

        if programme is not None:
            return programme
        else:
            return self._sync(pid)

    def _sync(self, pid):
        programme = Programmes.pull(pid)

        self._programmes_db.update({'pid': pid}, programme, upsert=True)

        return programme

    @staticmethod
    def pull(pid):
        url = 'https://www.bbc.co.uk/iplayer/episode/' + pid + '.json'
        json_data = json.loads(urllib2.urlopen(url).read())
        player_data = json_data['jsConf']['player']

        programme = {}

        programme['pid'] = player_data['pid']
        programme['title'] = player_data['title']
        programme['subtitle'] = player_data['subtitle']
        programme['masterbrand'] = player_data['masterbrand']

        return programme

