class Player:
    def __init__(self):
        self.awareness = 0
        self.ferry_trust = 0

        self.flags = {
            "met_ferryman": False,
            "heard_about_preacher": False
        }