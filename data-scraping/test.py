import inspect

def g():
    print("caller: ", inspect.stack()[-2].function)
        
class X:
    def __init__(self):
        self.__test = {}

    def f(self):
        return self.__test
    
    def h(self):
        t = self.f()
        t["test"] = 5

a = X()

print(a.f())
print(a.h())
print(a.f())