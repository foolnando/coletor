from Node import Node


class stack:
    def __init__(self):
        self.top = None
        self.size = 0


    def push(self, elem):
        pointer = self.top
        self.top = Node(elem)
        self.top.next = pointer
        self.size += 1

    def pop(self):
        pointer = self.top
        self.top = pointer.next
        self.size -= 1
    def topo(self):
        pointer = self.top.data
        return pointer
        

    def __str__(self):
        return self.__repr__()

pilha = stack()
pilha.push(2)
pilha.push(3)
pilha.push(4)
print(pilha.topo())
print(pilha.size)
pilha.pop()
print(pilha.topo())
print(pilha.size)