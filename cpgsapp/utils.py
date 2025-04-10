from collections import deque

class FixedFIFO:
    def __init__(self, max_size=5):
        self.queue = deque(maxlen=max_size)  # deque has built-in maxlen support
    
    def enqueue(self, item):
        self.queue.append(item)  # Automatically removes oldest item if full
    
    def dequeue(self):
        if not self.is_empty():
            return self.queue.popleft()
        raise IndexError("Queue is empty")
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def size(self):
        return len(self.queue)
    
    def get_queue(self):
        return list(self.queue)


