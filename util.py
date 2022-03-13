import time

class Util:

    def current_milli_time(self):
        return round(self.ms_from_secs(time.time()))

    def secs_from_ms(self, ms):
        return ms / 1000

    def ms_from_secs(self, seconds):
        return seconds * 1000

