class BattlesProcessor(object):

    def process(self, data):
        users = set()
        decks = []

        for battle in data:
            for user in battle['team']:
                decks.append(self.format_deckLink(user['deckLink']))
                users |= {user['tag']}

            for user in battle['opponent']:
                decks.append(self.format_deckLink(user['deckLink']))
                users |= {user['tag']}

        return dict(users=users, decks=decks)

    def format_deckLink(self, link: str):
        #42 = len("https://link.clashroyale.com/deck/en?deck=")
        return link[42:].split(';')
