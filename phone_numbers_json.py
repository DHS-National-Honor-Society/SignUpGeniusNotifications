import csv
import json 

with open('phones.csv', newline='') as csvfile:
    data = list(csv.reader(csvfile))

class Student:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone
    def __str__(self):
        return f"{self.name} {self.phone}"
    def toJson(self):
        return json.dumps(self.__dict__)

studentArray = []
for i in range(len(data)-1):
    string = f"{data[i+1][1]} {data[i+1][2]}"
    studentArray.append(Student(string, data[i+1][3]))

students = []
for i in studentArray:
  students.append(json.loads(i.toJson()))

csvfile.close()
with open("student_numbers.json","w") as jsonfile:
    jsonfile.write(json.dumps(students, ensure_ascii=False, indent=4))
