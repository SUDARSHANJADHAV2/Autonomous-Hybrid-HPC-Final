from .diagnostics.rules import diagnose
class Detector:
    def detect(self,event): return event
class Scaler:
    def recommend(self,event): return diagnose(event)
class Diagnostician:
    def analyze(self,event): return diagnose(event)
class Monitor:
    def summarize(self,health): return health
