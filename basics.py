# variables and data types


def greet(obj1,obj2):
    return obj1 + obj2



name = "faizan"
age = 30
is_learning = True
score = 94.3
myobj = {}
myarr = []
skills = ["JavaScript", "React", "HTML", "CSS", "Python"]
skills.append("AI Engineering")
skills.remove("CSS")
person = {
    "name": "Faizan",
    "age": 30,
    "skills": ["JavaScript", "React", "Python"],
    "is_learning_ai": True,
    "meta":{
        "hash":[101,"#learning"]
    }
}
# print(person["meta"]["hash"][0])
print(sum([person["meta"]["hash"][0],10]))
# print(name)
# print(age)
# print(is_learning)
# print(score)


# print(f"my name is {name.upper()}")
# for skill in skills:
#     print(f"I know: {skill}")

# print(type(age))
# print(type(is_learning))
# print(type(score))
# print(type(myobj))
# print(type(myarr))

