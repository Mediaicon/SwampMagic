class Player:
    def __init__(self):
        self.awareness = 0
        self.ferry_trust = 0

        self.flags = {
            "met_ferryman": False,
            "met_storekeeper": False,
            "heard_about_ferry_landing": False
        }

        self.journal = []