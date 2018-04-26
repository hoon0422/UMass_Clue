""" Module to crawl data about sections in UMass Amherst SPIRE.

This module has classes and methods to crawl data about class sections in UMass
Amherst SPIRE. All you need to do to execute this file properly is write proper
ID and password to log in to SPIRE.

"""

from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from bs4 import BeautifulSoup as BS
import traceback
import json
import time
import os, platform
from multiprocessing import Process
import re

DEBUG = True


class ClassCrawler:
    """ Crawler of data.

    This class represents a crawler. It has data and methods to access web pages in UMass Amherst SPIRE.

    Attributes:
        options: options for chrome driver.
        login_state: boolean data that shows whether the crawler is currently logged in SPIRE.
        major_keymap: dictionary for keymap of major. The key of dictionary is a key of major,
            and the value is the name of major.
        current_page: "__CurentPage" object. A flag for the currently accessing web page.
    """
    login_url = "https://www.spire.umass.edu/psp/heproda/?cmd=login&languageCd=ENG"
    class_url = "https://www.spire.umass.edu/psc/heproda/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL"

    class __CurrentPage:
        """ Flag for the current web page.

        This class represents a flag that shows what page the crawler accesses currently.

        Attributes:
            current: tells what page the crawler accesses currently.

        """
        NULL = "null"       # Not in the state of crawling.
        ENTRY = "entry"     # Entry page
        SEARCH = "search"   # Search result page
        DETAIL = "detail"   # Detail page for a section.

        def __init__(self):
            self.current = {
                self.NULL: True,
                self.ENTRY: False,
                self.SEARCH: False,
                self.DETAIL: False
            }

        def get_current_page(self):
            """
            Return what page the crawler accesses currently.
            :return: the page the crawler accesses currently.
            """
            for c in self.current.keys():
                if self.current[c] is True:
                    return c
            return self.NULL

        def go_to_entry(self):
            """
            Change the flag to the entry page.
            """
            self.__init_current()
            self.current[self.ENTRY] = True

        def go_to_search(self):
            """
            Change the flag to the search page.
            """
            self.__init_current()
            self.current[self.SEARCH] = True

        def go_to_detail(self):
            """
            Change the flag to the detail page.
            """
            self.__init_current()
            self.current[self.DETAIL] = True

        def go_to_null(self):
            """
            Change the flag to the null page.
            """
            self.__init_current()
            self.current[self.NULL] = True

        def __init_current(self):
            for c in self.current.keys():
                self.current[c] = False

    def __init__(self, options=None):
        self.options = options
        if platform.system() == 'Windows':
            self.driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options)
        elif platform.system() == 'Linux':
            self.driver = webdriver.Chrome('./chromedriver', chrome_options=options)
        else:
            raise ValueError("Unsupported Operating System.")
        self.login_state = False
        self.major_keymap = None
        self.current_page = ClassCrawler.__CurrentPage()

    def login(self, id: str, pw: str):
        """
        Make the crawler logged in SPIRE. After the call, the crawler will be on the entry page.
        :param id: ID to log in.
        :param pw: password to log in.
        :return: True if success, otherwise false.
        """

        # logging in
        self.driver.get(ClassCrawler.login_url)
        self.driver.find_element_by_name('userid').send_keys(id)
        self.driver.find_element_by_name('pwd').send_keys(pw)
        self.driver.find_element_by_name('Submit').click()

        # go to entry page.
        self.driver.get(ClassCrawler.class_url)
        self.__wait_for_going_to_entry()

        # Check whether the crawler is in entry page. If it is, then change flag. Otherwise, return false.
        if self.driver.find_element_by_id('pt_pageinfo_win0').get_attribute('page') == 'SSR_CLSRCH_ENTRY':
            self.current_page.go_to_entry()
            self.__update_major_keymap()
            self.login_state = True
            return True
        else:
            return False

    def progress_to_search(self, year: int, semester: str, career_str: str, major_idx: int):
        """
        Search sections. Before the call, the crawler must be on the entry page.
        After the call, the crawler will be on the search page.
        :param year: year for search.
        :param semester: semester for search.
        :param career_str: career for search.
        :param major_idx: the index of major for search.
        :return: true if success, otherwise false.
        """
        # check if the crawler is in the entry page.
        if self.current_page.get_current_page() is not self.current_page.ENTRY:
            if DEBUG:
                raise Exception()
            return False

        # year and semester
        self.driver.execute_script("document.getElementById('UM_DERIVED_SA_UM_TERM_DESCR')"
                                   ".setAttribute('onchange', '')")
        term_select = Select(self.driver.find_element_by_name('UM_DERIVED_SA_UM_TERM_DESCR'))
        term_select.select_by_visible_text(str(year) + ' ' + semester)

        # major
        self.driver.execute_script("document.getElementById('CLASS_SRCH_WRK2_SUBJECT$108$')"
                                   ".setAttribute('onchange', '')")
        course_select = Select(self.driver.find_element_by_name('CLASS_SRCH_WRK2_SUBJECT$108$'))
        course_select.select_by_index(major_idx)

        # career
        self.driver.execute_script("document.getElementById('CLASS_SRCH_WRK2_ACAD_CAREER')"
                                   ".setAttribute('onchange', '')")
        career_select = Select(self.driver.find_element_by_name('CLASS_SRCH_WRK2_ACAD_CAREER'))
        career_select.select_by_visible_text(career_str)

        # Uncheck 'search for open class only'.
        self.driver.find_element_by_name('CLASS_SRCH_WRK2_SSR_OPEN_ONLY').click()

        # Go to search page.
        self.driver.find_element_by_name('CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH').click()
        self.__wait_for_going_to_search()

        # Check if the crawler is on the search page. If it is, change the flag. Otherwise return false.
        if self.driver.find_element_by_id('pt_pageinfo_win0').get_attribute('page') == 'SSR_CLSRCH_RSLT':
            self.current_page.go_to_search()
            return True
        else:
            return False

    def progress_to_detail(self, section_idx: int):
        """
        Go to page about a section. Before this call, the crawler must be on the search page.
        After this call, the crawler will be on the detail page.
        :param section_idx: the index of the link for the detail page of a section.
        :return: True if success, otherwise false.
        """
        # check if the crawler is on the search page.
        if self.current_page.get_current_page() is not self.current_page.SEARCH:
            if DEBUG:
                raise Exception()
            return False

        # find the link to the specific search page.
        try:
            detail_element = self.driver.find_element_by_name('DERIVED_CLSRCH_SSR_CLASSNAME_LONG$' + str(section_idx))
        except NoSuchElementException:
            return False

        # Go to the detail page.
        detail_element.click()
        self.__wait_for_going_to_detail()

        # check if the crawler is on the detail page. If it is, change the flat. Otherwise, return false.
        if self.driver.find_element_by_id('pt_pageinfo_win0').get_attribute('page') == 'SSR_CLSRCH_DTL':
            self.current_page.go_to_detail()
            return True
        else:
            return False

    def return_to_search(self):
        """
        Return to the search page. Before the call, the crawler must be on the detail page.
        After this call, the crawler will be on the search page.
        :return: True if success, otherwise false.
        """
        # Check if the crawler is on the detail page.
        if self.current_page.get_current_page() is not self.current_page.DETAIL:
            if DEBUG:
                raise Exception()
            return

        # Go to the search page.
        view_search_result_btn = self.driver.find_element_by_name('CLASS_SRCH_WRK2_SSR_PB_BACK')
        view_search_result_btn.click()
        self.__wait_for_going_to_search()

        # Check if the crawler is on the search page. If it is, change the flag. Otherwise, return false.
        if self.driver.find_element_by_id('pt_pageinfo_win0').get_attribute('page') == 'SSR_CLSRCH_RSLT':
            self.current_page.go_to_search()
            return True
        else:
            return False

    def return_to_entry(self):
        """
        Return to the entry page. Before the call, the crawler must be on the search page.
        After the call, the crawler will be on the entry page.
        :return: True if success, otherwise false.
        """
        # Check if the crawler is on the search page.
        if self.current_page.get_current_page() is not self.current_page.SEARCH:
            if DEBUG:
                raise Exception()
            return

        # Go to the entry page.
        start_new_search_btn = self.driver.find_element_by_name('CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH')
        start_new_search_btn.click()
        self.__wait_for_going_to_entry()

        # Check if the crawler is on the entry page. If it is, change the flag. Otherwise, return false.
        if self.driver.find_element_by_id('pt_pageinfo_win0').get_attribute('page') == 'SSR_CLSRCH_ENTRY':
            self.current_page.go_to_entry()
            return True
        else:
            return False

    def clear_criteria(self):
        """
        Click a button to clear search criteria in the entry page. Before the call,
        the crawler must be on the entry page.
        :return: True if success, otherwise false.
        """
        # Check if the crawler is on the entry page.
        if self.current_page.get_current_page() is not self.current_page.ENTRY:
            if DEBUG:
                raise Exception()
            return False

        # Click the button
        self.driver.find_element_by_name('CLASS_SRCH_WRK2_SSR_PB_CLEAR').click()
        self.__wait_for_error_message_disappear()
        return True

    def __update_major_keymap(self):
        """
        Return the major keymap.
        :return: dictionary for keymap between major key and major name.
        """
        self.major_keymap = {}
        major_select = Select(self.driver.find_element_by_name('CLASS_SRCH_WRK2_SUBJECT$108$'))
        options = major_select.options[1:]
        for option in options:
            self.major_keymap[option.get_attribute('value')] = option.text

    def __wait_for_error_message_disappear(self):
        """
        If there is an error message in the entry page, wait for the message is disappeared.
        """
        WebDriverWait(self.driver, 60).until_not(
            EC.presence_of_element_located((By.ID, 'DERIVED_CLSMSG_ERROR_TEXT'))
        )

    def __wait_for_going_to_entry(self):
        """
        Wait for the entry web page loaded.
        """
        WebDriverWait(self.driver, 60).until(
            lambda driver: self.__wait_for_attribute_value(driver, (By.ID, 'pt_pageinfo_win0'),
                                                           'page', 'SSR_CLSRCH_ENTRY')
        )

    def __wait_for_going_to_search(self):
        """
        Wait for the search web page loaded.
        """
        WebDriverWait(self.driver, 60).until(
            lambda driver:
            self.__wait_for_attribute_value(driver, (By.ID, 'pt_pageinfo_win0'), 'page', 'SSR_CLSRCH_RSLT') or
            driver.find_element_by_id('DERIVED_CLSMSG_ERROR_TEXT')
        )

    def __wait_for_going_to_detail(self):
        """
        Wait for the detail web page loaded.
        """
        WebDriverWait(self.driver, 60).until(
            lambda driver: self.__wait_for_attribute_value(driver, (By.ID, 'pt_pageinfo_win0'),
                                                           'page', 'SSR_CLSRCH_DTL')
        )

    def __wait_for_attribute_value(self, driver, locator, attribute, value):
        """
        Wait for the attribute of the locator having the value in the current page.
        :param driver: the driver of the crawler. It must be a chrome driver.
        :param locator: tuple for how to find the locator. i.e. (By.ID, 'id_value').
        :param attribute: the name of the attribute.
        :param value: the expected value of the attribute.
        :return: true if the attribute has the expected value, otherwise false.
        """
        try:
            element_attribute = EC._find_element(driver, locator).get_attribute(attribute)
            return element_attribute == value
        except StaleElementReferenceException:
            return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()


class TimeUnit:
    """ Information of a time of a section.

    This class represents a time that a section has. It has data
    about what day the section holds on, what time the section starts, and
    what time the section ends. One section can have many "TimeUnit" objects.
    
    Attributes:
        day: day of a time of a section. Mo / Tu / We / Th / Fr / Sa / Su
        start_hour: hour when the section starts.
        start_min: minute when the section starts.
        end_hour: hour when the section ends.
        end_min: minute when the section ends.
    """
    def __init__(self):
        self.day = ""
        self.start_hour = -1
        self.start_min = -1
        self.end_hour = -1
        self.end_min = -1

    def time_to_dict(self):
        """
        Convert data in the object to dictionary format for JSON format.
        :return: Dictionary object that has data about time.
        """
        return {
            "day": self.day,
            "start_hour": self.start_hour,
            "start_min": self.start_min,
            "end_hour": self.end_hour,
            "end_min": self.end_min
        }


class Info:
    """ Information of a section

    This class has some methods that can crawl these data in class search HTML text in UMass Amherst SPIRE.
    It pre-processes the data and returns the data in dictionary format, which is easy to be changed in
    JSON format.

    The followings are components of a section in UMass Amherst.

    Attributes:
        year: 4-digit string
        semester: Spring / Summer / Fall / Winter
        career: Undergraduate / Graduate / Non-degree / Non-credit
        major: the major of a section
        course number: <major abbreviation> <some numbers or alphas>
        course title: the title of a course
        class number: 5-digit string
        category: the category of a section, i.e, lecture, laboratory, individual study, etc.
        lower unit: the minimum unit of a section.
        upper unit: the maximum unit of a section.
        components: the categories of another sections which must be enrolled with a section.
        professors: professors
        times: "TimeUnit" objects representing the class times.

    """
    def __init__(self):
        self.year = None
        self.semester = None
        self.career = None
        self.major = None
        self.course_num = None
        self.course_title = None
        self.class_num = None
        self.category = None
        self.lower_unit = None
        self.upper_unit = None
        self.components = None
        self.professors = None
        self.room = None
        self.times = None

    def crawl(self, html_text: str, major_keymap: dict):
        """
        Crawl data from class search HTML text in UMass Amherst SPIRE.
        :param html_text: class search HTML text in UMass Amherst SPIRE.
        :param major_keymap: keymap between major and major key.
        """
        html = BS(html_text, "html.parser")

        self.year = self.__preprocess_year(html.find("span", {"id": 'DERIVED_CLSRCH_SSS_PAGE_KEYDESCR'}))
        self.semester = self.__preprocess_semester(html.find("span", {"id": 'DERIVED_CLSRCH_SSS_PAGE_KEYDESCR'}))
        self.career = self.__preprocess_career(html.find("span", {"id": 'PSXLATITEM_XLATLONGNAME$33$'}))
        self.major = self.__preprocess_major(html.find("span", {"id": 'DERIVED_CLSRCH_DESCR200'}), major_keymap)
        self.course_num = self.__preprocess_course_num(html.find("span", {"id": 'DERIVED_CLSRCH_DESCR200'}))
        self.course_title = self.__preprocess_course_title(html.find("span", {"id": 'DERIVED_CLSRCH_DESCR200'}))
        self.class_num = self.__preprocess_class_num(html.find("span", {"id": 'SSR_CLS_DTL_WRK_CLASS_NBR'}))
        self.category = self.__preprocess_category(html.find("span", {"id": 'DERIVED_CLSRCH_SSS_PAGE_KEYDESCR'}))
        self.lower_unit, self.upper_unit = self.__preprocess_unit(
            html.find("span", {"id": 'SSR_CLS_DTL_WRK_UNITS_RANGE'})
        )
        self.components = self.__preprocess_components(html.select("span[id^='SSR_CLS_DTL_WRK_DESCR$']"))
        self.professors = self.__preprocess_professors(html.find("span", {"id": 'MTG_INSTR$0'}))
        self.room = self.__preprocess_room(html.find("span", {"id": 'MTG_LOC$0'}))
        self.times = self.__preprocess_times(html.find("span", {"id": 'MTG_SCHED$0'}))

    def get_info_dict(self):
        """
        Convert the data in this object to dictionary format.
        :return: dictionary containing the data of "Info" object.
        """
        return {
            "year": self.year,
            "semester": self.semester,
            "career": self.career,
            "major": self.major,
            "course_num": self.course_num,
            "course_title": self.course_title,
            "class_num": self.class_num,
            "category": self.category,
            "lower_unit": self.lower_unit,
            "upper_unit": self.upper_unit,
            "components": self.components,
            "professors": self.professors,
            "room": self.room,
            "times": self.times
        }

    @staticmethod
    def __preprocess_year(category_ele):
        """
        Extract year data from the parameter.
        :param category_ele: text from HTML containing data about year, semester, category.
        :return: year data of the section.
        """
        if category_ele is None:
            return 0
        semester_and_year = category_ele.text[category_ele.text.find('|') + 1: category_ele.text.rfind('|')].strip()
        return int(semester_and_year.split()[1])

    @staticmethod
    def __preprocess_semester(category_ele):
        """
        Extract semester data from the parameter.
        :param category_ele: text from HTML containing data about year, semester, category.
        :return: semester data of the section.
        """
        if category_ele is None:
            return 0
        semester_and_year = category_ele.text[category_ele.text.find('|') + 1: category_ele.text.rfind('|')].strip()
        return semester_and_year.split()[0]

    @staticmethod
    def __preprocess_career(career_ele):
        """
        Extract career data from the parameter.
        :param career_ele: text from HTML containing data about career.
        :return: career data of the section.
        """
        if career_ele is None:
            return ""
        return career_ele.text.strip()

    @staticmethod
    def __preprocess_major(course_ele, major_keymap: dict):
        """
        Extract major data from the parameter.
        :param course_ele: text from HTML containing data about course and major.
        :param major_keymap: keymap for major key and major name.
        :return: The name of the major of the section.
        """
        if course_ele is None:
            return ""
        return major_keymap[course_ele.text[:course_ele.text.find(' ')].strip()]

    @staticmethod
    def __preprocess_course_num(course_ele):
        """
        Extract course number from the parameter.
        :param course_ele: text from HTML containing data about course and major.
        :return: The number of the course of the section.
        """
        if course_ele is None:
            return ""
        course_num = course_ele.text[: course_ele.text.find('-', course_ele.text.find(' ') + 1)].strip()
        return re.sub(' +', ' ', course_num)

    @staticmethod
    def __preprocess_course_title(course_ele):
        """
        Extract course title from the parameter.
        :param course_ele: text from HTML containing data about course and major.
        :return: The title of the course of the section.
        """
        if course_ele is None:
            return ""
        bar_index = course_ele.text.find('-', course_ele.text.find(' ') + 1)
        space = course_ele.text.find(' ', bar_index + 2);
        return course_ele.text[space + 1:].strip()

    @staticmethod
    def __preprocess_class_num(class_num_ele):
        """
        Extract class number from the parameter.
        :param class_num_ele: text from HTML containing data about class number.
        :return: The class number of the section.
        """
        if class_num_ele is None:
            return ""
        return class_num_ele.text.strip()

    @staticmethod
    def __preprocess_category(category_ele):
        """
        Extract category from the parameter.
        :param category_ele: text from HTML containing data about year, semester, and category.
        :return: The category of the section.
        """
        if category_ele is None:
            return ""
        return category_ele.text[category_ele.text.rfind('|') + 2:].strip()

    @staticmethod
    def __preprocess_unit(unit_ele):
        """
        Extract lower unit and upper unit from the parameter.
        :param unit_ele: text from HTML containing data about unit.
        :return: the lower unit and the upper unit of the section.
        """
        if unit_ele is None:
            return 0, 0

        unit_str = unit_ele.text.strip()

        if len(unit_str) == 1:
            return int(unit_str), int(unit_str)

        lower_unit = unit_str[0:unit_str.find(' ')]
        upper_unit = unit_str[unit_str.rfind(' ') + 1:]
        return round(float(lower_unit), 1), round(float(upper_unit), 1)

    @staticmethod
    def __preprocess_components(component_eles):
        """
        Extract components from the parameter.
        :param component_eles: text from HTML containing data about components.
        :return: list of components of the section.
        """
        if len(component_eles) is 0:
            return []
        return [c.text.strip() for c in component_eles]

    @staticmethod
    def __preprocess_professors(professor_ele):
        """
        Extract professors from the parameter.
        :param professor_ele: text from HTML containing data about professors.
        :return: list of professors' name of the section.
        """
        if professor_ele is None:
            return ""
        return [professor.strip() for professor in professor_ele.text.split(',')]

    @staticmethod
    def __preprocess_room(room_ele):
        """
        Extract room from the parameter.
        :param room_ele: text from HTML containing data about room.
        :return: room data of the section.
        """
        if room_ele is None:
            return ""
        return room_ele.text.strip()

    @staticmethod
    def __preprocess_times(time_ele):
        """
        Extract times from the parameter
        :param time_ele: text from HTML containing data about time.
        :return: list of "TimeUnit" objects containing data about time of the section.
        """
        if time_ele is None:
            return ""

        time_str = time_ele.text.strip()
        if time_str == "TBA" or time_str == "" or time_str[0].isnumeric():
            # Invalid time (i.e. TBA, no data, on-line, etc.)
            return []

        first_space = time_str.find(' ')
        second_space = time_str.find(' ', first_space + 1)
        third_space = time_str.find(' ', second_space + 1)

        days = time_str[:first_space]
        start_time = time_str[first_space + 1: second_space]
        end_time = time_str[third_space + 1:]

        start_time_colon = start_time.find(':')
        start_time_hour = int(start_time[:start_time_colon])
        if start_time_hour < 12 and start_time[-2:] == "PM":
            start_time_hour += 12
        start_time_min = int(start_time[start_time_colon + 1: start_time_colon + 3])

        end_time_colon = end_time.find(':')
        end_time_hour = int(end_time[:end_time_colon])
        if end_time_hour < 12 and end_time[-2:] == "PM":
            end_time_hour += 12
        end_time_min = int(end_time[end_time_colon + 1: end_time_colon + 3])

        times = []
        for i in range(int(len(days) / 2)):
            day = days[2 * i: 2 * i + 2]
            time_unit = TimeUnit()
            time_unit.day = day
            time_unit.start_hour = start_time_hour
            time_unit.start_min = start_time_min
            time_unit.end_hour = end_time_hour
            time_unit.end_min = end_time_min
            times.append(time_unit.time_to_dict())

        return times


def crawl_data(
        id: str = "younghoonjeo",
        pw: str = "dudgns2@",
        class_file_name: str = 'classes.txt',
        log_file_name: str = 'log.txt',
        from_major_idx: int = 0,
        to_major_idx: int = 200,
        options=None
):
    """
    Crawl the data in UMass Amherst SPIRE.
    :param id: ID to log in.
    :param pw: password to log in.
    :param class_file_name: the name of the file containing data about sections.
    :param log_file_name: the name of the log file.
    :param from_major_idx: the index of the major from which crawling starts.
    :param to_major_idx: the index of the major to which crawling ends.
    :param options: options for chrome driver.
    """
    career_list = ['Undergraduate', 'Graduate', 'Non-Credit', 'Non-Degree']
    with ClassCrawler(options) as crawler:
        # log in and get the number of majors.
        crawler.login(id, pw)
        major_num = len(crawler.major_keymap)

        # update to_major_idx if it is larger than the number of majors.
        if to_major_idx > major_num:
            to_major_idx = major_num
        print(from_major_idx, "~", to_major_idx, " start")

        # check if there is 'raw' folder. If not, make one.
        raw_dir = os.path.join('..', 'raw')
        if not os.path.isdir(raw_dir):
            os.mkdir(raw_dir)

        # update the location of 'class_file_name' and 'log_file_name'
        class_file_name = os.path.join('..', 'raw', class_file_name)
        log_file_name = os.path.join('..', 'raw', log_file_name)

        # crawling
        info = Info()
        with open(class_file_name, mode='a', encoding='utf8')as class_file, open(log_file_name, mode='a') as log_file:
            try:
                for career in career_list:
                    for major_idx in range(from_major_idx, to_major_idx):
                        a = crawler.progress_to_search(2018, 'Spring', career, major_idx + 1)
                        log_file.write("Major idx: %d\n" % (major_idx + 1))
                        print("Major idx: %d" % (major_idx + 1))

                        if a is False:
                            crawler.clear_criteria()
                            continue
                        section_idx = 0

                        while crawler.progress_to_detail(section_idx):
                            info.crawl(crawler.driver.page_source, crawler.major_keymap)

                            # write the data in 'class.txt'. One section data per line.
                            class_file.write(json.dumps(info.get_info_dict(), ensure_ascii=False) + "\n")

                            # write the result in log file. One result per line.
                            log_file.write(
                                str(time.time()) + " - Career: " + career
                                + " / Major: " + info.major
                                + " / Class#: " + info.class_num + "\n"
                            )
                            print(
                                str(time.time()) + " - Career: " + career
                                + " / Major: " + info.major
                                + " / Class#: " + info.class_num
                            )
                            crawler.return_to_search()
                            section_idx += 1

                        crawler.return_to_entry()

            except Exception as ex:
                traceback.print_exc()
                log_file.write(traceback.format_exc())

    print(from_major_idx, "~", to_major_idx, " end")


if __name__ == "__main__":
    print("start crawling")
    time.sleep(3)
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    # uni-processing
    crawl_data(options=options)

    # multiprocessing
    '''
    major_num = 0

    with ClassCrawler(options) as major_num_crawler:
        major_num_crawler.login("younghoonjeo", "dudgns2@")
        major_num = len(major_num_crawler.major_keymap)

    print("major_num:", major_num)

    start = 0
    end = 0
    for i in range(1, 3):
        start = end
        end = int(major_num / 2) * i
        if i == 2:
            end = major_num
        class_file = str(start) + "-" + str(end) + "_classes.txt"
        log_file = str(start) + "-" + str(end) + "_log.txt"
        Process(target=crawl_data, args=(class_file, log_file, start, end, options)).start()
    '''

    print("end crawling!")
