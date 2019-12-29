

class Entry(object):
    def __init__(self, user, json):
        self.user = user
        self.id = json['id']
        self.uri = json['uri']
        self.duration = json['duration_ms']
        self.track = json['name']
        self.artists = json['artists'][0]['name']
        self.album = json['album']['name']
        self.art_s = json['album']['images'][2]['url']
        self.art_m = json['album']['images'][1]['url']
        self.upvotes = set()
        self.downvotes = set()
    
    def upvote(self, user):
        self.upvotes.add(user)
        if user in self.downvotes:
            self.downvotes.remove(user)
    
    @property
    def ups(self):
        return len(self.upvotes)
    
    def downvote(self, user):
        self.downvotes.add(user)
        if user in self.upvotes:
            self.upvotes.remove(user)
    
    @property
    def downs(self):
        return len(self.downvotes)
    
    def __lt__(self, other):
        ''' Less than operator
        Used for sorting
        '''
        if not isinstance(other, type(self)):
            ret = NotImplemented
        else:
            ret = (self.ups, -self.downs) > (other.ups, -other.downs)
        return ret

json = {}
json['id'] = 'xxxxx'
json['uri'] = 'spotify:track:xxxxx'
json['duration_ms'] = 10000
json['name'] = 'Track'
json['artists'] = [{'name' : 'Artist'}]
json['album'] = {'name' : 'Album'}
json['album']['images'] = [{'url':'../static/images/album.png'}]*3
default_entry = Entry('Wiggles', json)

class Queue(list):
    def add(self, user, json):
        self.append(Entry(user, json))
        
    def sort(self, key=None, reverse=False):
        if self.__len__() < 2:
            pass
        else:
            # playing = self.__getitem__(0)
            npslice = slice(1, None)
            queue = self.__getitem__(npslice)
            queue.sort()
            self.__setitem__(npslice, queue)
            
        
