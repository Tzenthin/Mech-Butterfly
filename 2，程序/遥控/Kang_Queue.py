class Queue:
    def __init__(self):
        self.items = []
 
    def is_empty(self):
        return len(self.items) == 0
 
    def enqueue(self, item):
        self.items.append(item)
 
    def dequeue(self):
        if self.is_empty():
            raise Exception('Queue is empty')
        return self.items.pop(0)
 
    def size(self):
        return len(self.items)
    
    def average(self):
        return sum(self.items)/len(self.items)
    
if __name__ == "__main__":
    q = Queue()
    for i in range(5):
        q.enqueue(i)
    print(q.items)
    q.dequeue()
    print(q.items)
    print(q.average())