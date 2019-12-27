

class Entry(object):
    def __init__(self, user, json):
        self.user = user
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
    
    def downvote(self, user):
        self.downvotes.add(user)
        if user in self.upvotes:
            self.upvotes.remove(user)


class Queue(list):
    def add(self, user, json):
        self.append(Entry(user, json))
        
