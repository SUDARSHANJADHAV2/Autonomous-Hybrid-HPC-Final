from collections import deque
class EventBus:
    def __init__(self): self.q=deque()
    def publish(self,event): self.q.append(event)
    def get(self): return self.q.popleft() if self.q else None
