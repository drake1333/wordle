# class bb:
#     def __init__(self,nom):
#         self.nom = nom
        
#     def take(self,take):
        
#         print(take)

# class cc(bb):
#     def __init__(self, nom):
#         super().__init__(nom)     
        
#     def hh(self):
#         print("h")
    
# dfgd = bb("kk")
# pp = cc()
# pp.take("g")

class Parrot:

    def fly(self):
        print('Parrot can fly')

    def swim(self):
        print('Parrot can not swim')

class Penguin:

    def fly(self):
        print('Penguin can not fly')

    def swim(self):
        print('Penguin can swim')

# common interface
def flying_test(bird):
    bird.fly()

#instantiate objects
blu = Parrot()
peggy = Penguin()

# passing the object
flying_test(blu)
flying_test(peggy)