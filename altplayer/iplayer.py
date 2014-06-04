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

        programme = {}
        programme['pid'] = json_data['jsConf']['player']['pid']
        programme['title'] = json_data['jsConf']['player']['title']
        programme['subtitle'] = json_data['jsConf']['player']['subtitle']

        return programme

