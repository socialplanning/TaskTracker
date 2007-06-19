class DummyEventServer:
    def send_message(self, *args):
        pass
    def queue(self, name):
        return self
