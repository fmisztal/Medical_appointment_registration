import requests
import os
import platform


BASE = "http://127.0.0.1:5000/"
# List of available doctors
DOCTORS = ["Mariusz Nowak", "Marzena Borowik", "Jan Kowalski", "Stanislaw Nowak", "Adam Nadobny", "Piotr Krzyszczak"]

# initialization of empty dictionary
DATA = dict.fromkeys(['patient_id', 'patient_name', 'doctor_name', 'visit_date'])


def clear_screen():
    """Function to clear terminal

    Function checks which system program is running on
    """

    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


def visit_to_string(dictionary):
    """Visit's data serialization

    Function converts visit's data to string

    :param dictionary: Dictionary with visit's data
    :type dictionary: dict
    :return: a string of visit's data
    :rtype: str
    """

    visit_string = ''
    for visits in range(len(dictionary)):
        visit_string += f"Visit id: {dictionary[visits]['visit_id']}," \
                        f" Visit date: 20{(int(dictionary[visits]['visit_date'] / 1000000)) - 100}/" \
                        f"{(int(dictionary[visits]['visit_date'] / 10000) % 100)}" \
                        f"/{(int(dictionary[visits]['visit_date'] / 100) % 100)}" \
                        f" {(int(dictionary[visits]['visit_date']) % 100)}.00," \
                        f" Patient id: {dictionary[visits]['patient_id']}," \
                        f" Patient name: {dictionary[visits]['patient_name']}," \
                        f" Doctor's name: {dictionary[visits]['doctor_name']}\n\n"
    return visit_string


def make_appointment():
    """Create new appointment

    Function asks user for visit's data. Function call data_check to check if date format is correct. If it is right,
    make new visit in database and show information from server as dictionary value.
    """

    clear_screen()
    is_right = True

    patient_id = int(input("Enter your id: "))
    check = id_check(patient_id)
    if check[1]:
        DATA['patient_id'] = check[0]
    else:
        is_right = False

    patient_name = input("Enter your name and surname: ")
    DATA['patient_name'] = patient_name

    print("Available doctors")
    print(*DOCTORS, sep=", ")
    doctor_name = input("Enter doctor's name and surname: ")
    check = check_doctor(doctor_name)
    if check[1]:
        DATA['doctor_name'] = check[0]
    else:
        is_right = False

    visit_date = input("Enter visit date (YYMMDDHH): ")
    visit_date = int("1" + visit_date)  # we have to add one in case the year is less than 2010,
                                        # (for example with 09 when converting to int "cut" would be 0
    check = date_check(visit_date)
    if check[1]:
        DATA['visit_date'] = check[0]
    else:
        is_right = False

    if is_right:
        response = requests.post(BASE + 'visit', DATA)
        if 'error' in response.json():
            print(response.json()["error"])
        else:
            print(response.json()["message"])


def show():
    """Show available search modes and display visits

    User decide how does he want to search visit and choose method by typing number.
    Function use method GET and uses appropriate parameters in URL.
    Function prints server response as dictionary value.
    """

    clear_screen()
    print("Available search modes:")
    print("1. Show all")
    print("2. Search by id numer")
    print("3. Search by doctor's name")
    print("4. Search by visit date")
    print("5. Search for a specific visit")

    how_to_show = int(input("Choose search mode: "))
    print("\n")
    if how_to_show == 1:
        response = requests.get(BASE + 'visit/all')
        if 'error' in response.json():
            print(response.json()["error"])
        else:
            print(visit_to_string(response.json()))
    elif how_to_show == 2:
        patient_id = int(input("Enter your id: "))
        response = requests.get(BASE + 'visit/patient', {'patient_id': patient_id})
        if 'error' in response.json():
            print(response.json()["error"])
        else:
            print(visit_to_string(response.json()))
    elif how_to_show == 3:
        doctor_name = input("Enter doctor's name: ")
        response = requests.get(BASE + 'visit/doctor', {'doctor_name': doctor_name})
        if 'error' in response.json():
            print(response.json()["error"])
        else:
            print(visit_to_string(response.json()))
    elif how_to_show == 4:
        visit_date = input("Enter date (YYMMDDHH): ")
        visit_date = int("1" + visit_date)
        response = requests.get(BASE + 'visit/date', {'visit_date': visit_date})
        if 'error' in response.json():
            print(response.json()["error"])
        else:
            print(visit_to_string(response.json()))
    elif how_to_show == 5:
        patient_id = int(input("Enter your id: "))
        doctor_name = input("Enter doctor's name: ")
        visit_date = input("Enter date (YYMMDDHH): ")
        visit_date = int("1" + visit_date)
        response = requests.get(BASE + 'visit/selected', {'patient_id': patient_id, 'doctor_name': doctor_name,
                                                          'visit_date': visit_date})
        if 'error' in response.json():
            print(response.json()["error"])
        else:
            print(visit_to_string(response.json()))
    else:
        print("Cannot be selected")


def delete():
    """Delete one visit

    Delete visit based on visit id.
    Function uses DELETE method with appropriate parameter in URL and deletes visit.
    Function prints server response as dictionary value.
    """

    clear_screen()
    visit_to_delete = int(input("Enter the id of the visit you want to delete: "))
    response = requests.delete(BASE + f'visit/{visit_to_delete}')
    if 'error' in response.json():
        print(response.json()["error"])
    else:
        print(response.json()["message"])


def delete_all():
    """Delete all visits

    Function uses DELETE method and deletes all visits.
    Function prints server response as dictionary value.
    """

    clear_screen()
    response = requests.delete(BASE + f'visit')
    print(response.json()["message"])


def date_check(date):
    """Checks if date is in right format

    Function, in loop, checks if date is possible (01 <= day <= 31,01 <= month <= 12, 00 < year <99).
    Checks if time is the time given is within the working hours of the hospital (8-18).
    If is not user can type correct date and time.
    If date and time will be correct function will return this information

    :param date: given date and time as number
    :type date: int
    :return: list of 2 arguments; date and if it is in right format or not
    :rtype: list
    """

    while True:
        is_right = True
        if date > 199123124 or date < 100010100:
            is_right = False
            print("Wrong date format")
            decision = input("Do you want try again? [y/n]: ")
            if decision == 'y':
                date = input("Enter visit date (YYMMDDHH): ")
                date = int("1" + date)
                continue
            return [date, is_right]
        if date % 100 > 18 or date % 100 < 8:
            is_right = False
            print("At this time hospital is closed")
            decision = input("Do you want try again? [y/n]: ")
            if decision == 'y':
                date = input("Enter visit date (YYMMDDHH): ")
                date = int("1" + date)
                continue
            return [date, is_right]

        if int(date / 10000) % 100 > 12 or int(date / 100) % 100 > 31:
            is_right = False
            print("Impossible date")
            decision = input("Do you want try again? [y/n]: ")
            if decision == 'y':
                date = input("Enter visit date (YYMMDDHH): ")
                date = int("1" + date)
                continue

        return [date, is_right]


def id_check(patient_id):
    """Checks if patient id is in right format

    Function, in loop, checks if patient id has 11 numbers and allows user to type correct one.

    :param patient_id: given patient id
    :type patient_id: int
    :return: list of 2 arguments; patient id and if it is in right format or not
    :rtype: list
    """

    while True:
        is_right = True
        if patient_id < 10000000000 or patient_id > 99999999999:
            is_right = False
            print("Wrong id, it should have 11 numbers")
            decision = input("Do you want try again? [y/n]: ")
            if decision == 'y':
                patient_id = int(input("Enter id: "))
                continue
        return [patient_id, is_right]


def check_doctor(doctor_name):
    """Check if doctor is available

    Function, in loop, checks if doctor name and surname in doctor list (DOCTORS) and allows user to type correct one.

    :param doctor_name: given doctor name and surname
    :type doctor_name: str
    :return: list of 2 arguments; doctor name nad surname and if doctor is available or not
    :rtype: list
    """
    while True:
        is_right = True
        if doctor_name not in DOCTORS:
            is_right = False
            print("This doctor is not available")
            decision = input("Do you want try again? [y/n]: ")
            if decision == 'y':
                print("Available doctors")
                print(*DOCTORS, sep=", ")
                doctor_name = input("Enter doctor name and surname: ")
                continue
        return [doctor_name, is_right]


def menu_system():
    """Display menu, user can choose action

    Display avaible options (Make an appointment, Show an appointment, Delete an appointment, Delete all).
    User can type appropriate number.
    Function calls another action functions.

    :raises TypeError: if user types wrong type
    """

    while True:
        clear_screen()
        print("Available actions:")
        print("1. Make an appointment")
        print("2. Show an appointment")
        print("3. Delete an appointment")
        print("4. Delete all")
        action = int(input("Choose action: "))
        if action == 1:
            try:
                make_appointment()
            except:
                print("Wrong type, insert numbers")
        elif action == 2:
            try:
                show()
            except:
                print("Wrong type, insert numbers")
        elif action == 3:
            try:
                delete()
            except:
                print("Wrong type, insert numbers")
        elif action == 4:
            delete_all()
        else:
            print("No such action")
        program_loop = input("Do you want to continue? [yes/no]: ")
        if program_loop == "yes":
            continue
        break


try:
    menu_system()
except:
    print("Something went wrong")



