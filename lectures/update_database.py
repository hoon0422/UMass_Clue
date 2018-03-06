import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UMass_Clue.settings")

import django
django.setup()

from lectures.models import *
import json
import datetime


def get_data(file_name: str):
    infos = []
    with open(file_name, 'r', encoding='utf8') as file:
        data_str_list = file.read().strip().split('\n')
        for data_str in data_str_list:
            infos.append(json.loads(data_str))
    return infos


def save_query(info: dict):
    year_and_semester, _ = YearAndSemester.objects.get_or_create(year=info["year"], semester=info["semester"])

    career, _ = Career.objects.get_or_create(title=info["career"])

    major, _ = Major.objects.get_or_create(title=info["major"])

    category, _ = Category.objects.get_or_create(title=info["category"])

    course, _ = Course.objects.get_or_create(title=info["course_title"], major=major, career=career,
                                             category=category, course_num=info["course_num"],
                                             year_and_semester=year_and_semester)

    room, _ = Room.objects.get_or_create(name=info["room"])

    session, _ = Session.objects.get_or_create(class_num=info["class_num"], room=room, course=course,
                                               upper_unit=info["upper_unit"], lower_unit=info["lower_unit"])

    for info_professor in info["professors"]:
        professor, _ = Professor.objects.get_or_create(name=info_professor)
        session.professors.add(professor)

    for info_time in info["times"]:
        start_time = datetime.time(info_time["start_hour"], info_time["start_min"], 0, 0)
        end_time = datetime.time(info_time["end_hour"], info_time["end_min"], 0, 0)
        time, _ = DayTimeField.objects.get_or_create(day=info_time["day"], start_time=start_time,
                                                     end_time=end_time)
        session.times.add(time)

    for info_component in info["components"]:
        component, _ = Category.objects.get_or_create(title=info_component)
        session.components.add(component)


infos = get_data("C:\\Users\\Administrator\\Desktop\\Younghoon_Jeong\\djangoPrac\\UMass_Clue\\UMass_Clue\\raw\\classes.txt")
for info in infos:
    save_query(info)
