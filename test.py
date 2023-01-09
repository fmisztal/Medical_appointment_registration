import requests

"""Add 5 users to database
"""

BASE = "http://127.0.0.1:5000/"

data = [{"visit_date": 112123012, "patient_id": 12345678934, "patient_name": "Jan Kowalski",
         "doctor_name": "Marzena Borowik"},
        {"visit_date": 111121107, "patient_id": 98765432134, "patient_name": "Jan Kowalski",
         "doctor_name": "Stanislaw Nowak"},
        {"visit_date": 122102208, "patient_id": 24682333156, "patient_name": "Marcelina Doborowska",
         "doctor_name": "Adam Nadobny"},
        {"visit_date": 114090909, "patient_id": 31415928624, "patient_name": "Przemek Wolinski",
         "doctor_name": "Piotr Krzyszczak"},
        {"visit_date": 122040412, "patient_id": 11111111143, "patient_name": "Jan Buczek",
         "doctor_name": "Marzena Borowik"},
        {"visit_date": 112080816, "patient_id": 12345678934, "patient_name": "Jan Kowalski",
         "doctor_name": "Adam Nadobny"}]

for i in data:
    response = requests.post(BASE + "visit", i)
    print(response.json())
