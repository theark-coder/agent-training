# user = {
#     "name": "Jack",
#     "age": 20,
#     "role": "AI Engineer",}
# user["age"]=22
# user["city"]="Tokyo"
# del user["age"]
# for key, value in user.items():
#     print(key,value)
# 
# class User:

#     def __init__(self, name, age):
#         self.name = name
#         self.age = age
#     def introduce(self) :
#         print (f"My name is {self.name},I am {self.age} years old")  
# user = User("Jack", 22)
from dataclasses import dataclass
@dataclass
class User:
    name: str
    age: int
    role: str
user1 = User("Jack", 22, "AI Engineer")
user2 = User("Tom", 25, "Backend Engineer")
users = [user1, user2]
for user in users:
    print(user.name)
    print(user.role)    
