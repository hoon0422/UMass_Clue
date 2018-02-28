from bs4 import BeautifulSoup
from .models import *
import datetime


class TimeUnit:
    day = ""
    start_hour = -1
    start_min = -1
    end_hour = -1
    end_min = -1


def crawl_data(html_text):
    html = BeautifulSoup(html_text, "html_parser")
    category = html.find("span", {"id": 'DERIVED_CLSRCH_SSS_PAGE_KEYDESCR'})
    course = html.find("span", {"id": 'DERIVED_CLSRCH_DESCR200'})
    class_num = html.find("span", {"id": 'SSR_CLS_DTL_WRK_CLASS_NBR'})
    unit_str = html.find("span", {"id": 'SSR_CLS_DTL_WRK_UNITS_RANGE'})
    career = html.find("span", {"id": 'PSXLATITEM_XLATLONGNAME$33$'})
    components = html.select("span[id^='SSR_CLS_DTL_WRK_DESCR$']")
    professors = html.find("span", {"id": 'MTG_INSTR$0'})
    room = html.find("span", {"id": 'MTG_LOC$0'})
    time_str = html.find("span", {"id": 'MTG_SCHED$0'})

    category = category.text[category.text.rfind('|') + 2:]
    first_space = course.text.find(' ')
    major_str = course.text[:first_space]
    course_num = course.text[first_space + 1: course.text.find('-')]
    course_title = course.text[course.text.find('-') + 4:]
    class_num = class_num.text
    unit_str = unit_str.text
    career = career.text
    components = [c.text.strip() for c in components]
    professors = professors.text
    room = room.text
    time_str = time_str.text

    return {
        "category": category.strip(),
        "major": major_str.strip(),
        "course_num": course_num.strip(),
        "course_title": course_title.strip(),
        "class_num": class_num.strip(),
        "unit_str": unit_str.strip(),
        "career": career.strip(),
        "components": components,
        "professors": professors.strip(),
        "room": room.strip(),
        "time_str": time_str.strip()
    }


def time_str_to_times(time_str: str):
    if time_str == "TBA":
        return []

    first_space = time_str.find(' ')
    second_space = time_str.find(' ', first_space + 1)
    third_space = time_str.find(' ', second_space + 1)

    days = time_str[:first_space]
    start_time = time_str[first_space + 1: second_space]
    end_time = time_str[third_space + 1:]

    start_time_colon = start_time.find(':')
    start_time_hour = int(start_time[:start_time_colon]) + (12 if start_time[-2:] == "PM" else 0)
    start_time_min = int(start_time[start_time_colon + 1: start_time_colon + 3])

    end_time_colon = end_time.find(':')
    end_time_hour = int(end_time[:end_time_colon]) + (12 if end_time[-2:] == "PM" else 0)
    end_time_min = int(end_time[end_time_colon + 1: end_time_colon + 3])

    times = []
    for i in range(len(days), step=2):
        day = days[i: i + 2]
        time_unit = TimeUnit()
        time_unit.day = day
        time_unit.start_hour = start_time_hour
        time_unit.start_min = start_time_min
        time_unit.end_hour = end_time_hour
        time_unit.end_min = end_time_min
        times.append(time_unit)

    return times


def major_key_to_major(major_key: str):
    pass


def unit_str_to_unit(unit_str: str):
    if len(unit_str) == 1:
        return int(unit_str), int(unit_str)

    lower_unit = unit_str[0:unit_str.find(' ')]
    upper_unit = unit_str[unit_str.rfind(' ') + 1:]
    return lower_unit, upper_unit


def html_to_query(html_text: str, year: int, semester: str):
    info = crawl_data(html_text)

    # time
    info["times"] = time_str_to_times(info["time_str"])
    del info["time_str"]

    # major
    info["major"] = major_key_to_major(info["major"])

    # unit
    lower_unit, upper_unit = unit_str_to_unit(info["unit_str"])
    info["lower_unit"] = lower_unit
    info["upper_unit"] = upper_unit
    del info["unit_str"]

    # year, semester
    info["year"] = year
    info["semester"] = semester

    return info


def save_query(info: dict):
    career = Career.objects.filter(title=info["career"])
    if len(career) is 0:
        career = Career(title=info["career"])
        career.save()

    major = Major.objects.filter(title=info["major"])
    if len(major) is 0:
        major = Major(title=info["major"])
        major.save()

    category = Category.objects.filter(title=info["category"])
    if len(category) is 0:
        category = Category(title=info["category"])
        category.save()

    year_and_semester = YearAndSemester.objects.filter(year=info["year"], semester=info["semester"])
    if len(year_and_semester) is 0:
        year_and_semester = YearAndSemester(year=info["year"], semester=info["semester"])
        year_and_semester.save()

    course = Course.objects.filter(major=major, course_num=info["course_num"], year_and_semester=year_and_semester)
    if len(course) is 0:
        course = Course(title=info["course_title"], major=major, career=career,
                        category=category, course_num=info["course_num"], upper_unit=info["upper_unit"],
                        lower_unit=["lower_unit"], year_and_semester=year_and_semester)
        course.save()

    professors = []
    for info_professor in info["professors"]:
        professor = Professor.objects.filter(name=info_professor)
        if len(professor) is 0:
            professor = Professor(name=info_professor)
            professor.save()
        professors.append(professor)

    building = Building.objects.filter(name=info["building"])
    if len(building) is 0:
        building = Building(name=info["building"])
        building.save()

    times = []
    for info_time in info["times"]:
        time = DayTimeField.objects.filter(day=info_time.day, start_time__hour=info_time.start_hour,
                                           start_time__minute=info_time.start_min, end_time__hour=info_time.end_hour,
                                           end_time__minute=info_time.end_min)
        if len(time) is 0:
            time = DayTimeField(day=info_time.day,
                                start_time=datetime.time(info_time.start_hour, info_time.start_min, 0),
                                end_time=datetime.time(info_time.end_hour, info_time.end_min, 0))
            time.save()
        times.append(time)

    session = Session.objects.filter(class_num=info["class_num"])
    if len(session) is 0:
        session = Session(class_num=info["class_num"], building=building, course=course)
        session.save()
        for prof in professors:
            session.professors.add(prof)
        for time in times:
            session.times.add(time)
