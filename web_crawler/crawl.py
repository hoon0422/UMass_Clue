from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from bs4 import BeautifulSoup as BS
import traceback
import json
import time
from multiprocessing import Process

DEBUG = True


class ClassCrawler:
    login_url = "https://www.spire.umass.edu/psp/heproda/?cmd=login&languageCd=ENG"
    class_url = "https://www.spire.umass.edu/psc/heproda/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL"

    class __CurrentPage:
        NULL = "null"
        ENTRY = "entry"
        SEARCH = "search"
        DETAIL = "detail"

        def __init__(self):
            self.current = {
                self.NULL: True,
                self.ENTRY: False,
                self.SEARCH: False,
                self.DETAIL: False
            }

        def get_current_page(self):
            for c in self.current.keys():
                if self.current[c] is True:
                    return c
            return self.NULL

        def go_to_entry(self):
            self.__init_current()
            self.current[self.ENTRY] = True
            pass

        def go_to_search(self):
            self.__init_current()
            self.current[self.SEARCH] = True
            pass

        def go_to_detail(self):
            self.__init_current()
            self.current[self.DETAIL] = True
            pass

        def go_to_null(self):
            self.__init_current()
            self.current[self.NULL] = True
            pass

        def __init_current(self):
            for c in self.current.keys():
                self.current[c] = False

    def __init__(self, options=None):
        self.options = options
        self.driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options)
        self.login_state = False
        self.major_keymap = None
        self.current_page = ClassCrawler.__CurrentPage()

    def login(self, id: str, pw: str):
        self.driver.get(ClassCrawler.login_url)
        self.driver.find_element_by_name('userid').send_keys(id)
        self.driver.find_element_by_name('pwd').send_keys(pw)
        self.driver.find_element_by_name('Submit').click()

        self.driver.get(ClassCrawler.class_url)

        self.__wait_for_going_to_entry()
        if self.driver.find_element_by_id('pt_pageinfo_win0').get_attribute('page') == 'SSR_CLSRCH_ENTRY':
            self.current_page.go_to_entry()
        else:
            return False

        self.__update_major_keymap()
        self.login_state = True
        return True

    def progress_to_search(self, year: int, semester: str, career_str: str, major_idx: int):
        if self.current_page.get_current_page() is not self.current_page.ENTRY:
            if DEBUG:
                raise Exception()
            return False

        self.driver.execute_script("document.getElementById('UM_DERIVED_SA_UM_TERM_DESCR')"
                                   ".setAttribute('onchange', '')")
        term_select = Select(self.driver.find_element_by_name('UM_DERIVED_SA_UM_TERM_DESCR'))
        term_select.select_by_visible_text(str(year) + ' ' + semester)

        self.driver.execute_script("document.getElementById('CLASS_SRCH_WRK2_SUBJECT$108$')"
                                   ".setAttribute('onchange', '')")
        course_select = Select(self.driver.find_element_by_name('CLASS_SRCH_WRK2_SUBJECT$108$'))
        course_select.select_by_index(major_idx)

        self.driver.execute_script("document.getElementById('CLASS_SRCH_WRK2_ACAD_CAREER')"
                                   ".setAttribute('onchange', '')")
        career_select = Select(self.driver.find_element_by_name('CLASS_SRCH_WRK2_ACAD_CAREER'))
        career_select.select_by_visible_text(career_str)

        self.driver.find_element_by_name('CLASS_SRCH_WRK2_SSR_OPEN_ONLY').click()

        self.driver.find_element_by_name('CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH').click()
        self.__wait_for_going_to_search()
        if self.driver.find_element_by_id('pt_pageinfo_win0').get_attribute('page') == 'SSR_CLSRCH_RSLT':
            self.current_page.go_to_search()
        else:
            return False

        return True

    def progress_to_detail(self, section_idx: int):
        if self.current_page.get_current_page() is not self.current_page.SEARCH:
            if DEBUG:
                raise Exception()
            return False

        try:
            detail_element = self.driver.find_element_by_name('DERIVED_CLSRCH_SSR_CLASSNAME_LONG$' + str(section_idx))
        except NoSuchElementException:
            return False

        detail_element.click()
        self.__wait_for_going_to_detail()
        if self.driver.find_element_by_id('pt_pageinfo_win0').get_attribute('page') == 'SSR_CLSRCH_DTL':
            self.current_page.go_to_detail()
        else:
            return False

        return True

    def return_to_search(self):
        if self.current_page.get_current_page() is not self.current_page.DETAIL:
            if DEBUG:
                raise Exception()
            return

        view_search_result_btn = self.driver.find_element_by_name('CLASS_SRCH_WRK2_SSR_PB_BACK')

        view_search_result_btn.click()
        self.__wait_for_going_to_search()
        if self.driver.find_element_by_id('pt_pageinfo_win0').get_attribute('page') == 'SSR_CLSRCH_RSLT':
            self.current_page.go_to_search()
        else:
            return False
        return True

    def return_to_entry(self):
        if self.current_page.get_current_page() is not self.current_page.SEARCH:
            if DEBUG:
                raise Exception()
            return

        start_new_search_btn = self.driver.find_element_by_name('CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH')

        start_new_search_btn.click()
        self.__wait_for_going_to_entry()

        if self.driver.find_element_by_id('pt_pageinfo_win0').get_attribute('page') == 'SSR_CLSRCH_ENTRY':
            self.current_page.go_to_entry()
        else:
            return False
        return True

    def clear_criteria(self):
        if self.current_page.get_current_page() is not self.current_page.ENTRY:
            if DEBUG:
                raise Exception()
            return False

        self.driver.find_element_by_name('CLASS_SRCH_WRK2_SSR_PB_CLEAR').click()
        self.__wait_for_error_message_disappear()

    def __update_major_keymap(self):
        self.major_keymap = {}
        major_select = Select(self.driver.find_element_by_name('CLASS_SRCH_WRK2_SUBJECT$108$'))
        options = major_select.options[1:]
        for option in options:
            self.major_keymap[option.get_attribute('value')] = option.text

    def __wait_for_error_message_disappear(self):
        WebDriverWait(self.driver, 60).until_not(
            EC.presence_of_element_located((By.ID, 'DERIVED_CLSMSG_ERROR_TEXT'))
        )

    def __wait_for_going_to_entry(self):
        WebDriverWait(self.driver, 60).until(
            lambda driver: self.__wait_for_attribute_value(driver, (By.ID, 'pt_pageinfo_win0'),
                                                           'page', 'SSR_CLSRCH_ENTRY')
        )

    def __wait_for_going_to_search(self):
        WebDriverWait(self.driver, 60).until(
            lambda driver:
            self.__wait_for_attribute_value(driver, (By.ID, 'pt_pageinfo_win0'), 'page', 'SSR_CLSRCH_RSLT') or
            driver.find_element_by_id('DERIVED_CLSMSG_ERROR_TEXT')
        )

    def __wait_for_going_to_detail(self):
        WebDriverWait(self.driver, 60).until(
            lambda driver: self.__wait_for_attribute_value(driver, (By.ID, 'pt_pageinfo_win0'),
                                                           'page', 'SSR_CLSRCH_DTL')
        )

    def __wait_for_attribute_value(self, driver, locator, attribute, value):
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
    def __init__(self):
        self.day = ""
        self.start_hour = -1
        self.start_min = -1
        self.end_hour = -1
        self.end_min = -1

    def time_to_dict(self):
        return {
            "day": self.day,
            "start_hour": self.start_hour,
            "start_min": self.start_min,
            "end_hour": self.end_hour,
            "end_min": self.end_min
        }


class Info:
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
        if category_ele is None:
            return 0
        semester_and_year = category_ele.text[category_ele.text.find('|') + 1: category_ele.text.rfind('|')].strip()
        return int(semester_and_year.split()[1])

    @staticmethod
    def __preprocess_semester(category_ele):
        if category_ele is None:
            return 0
        semester_and_year = category_ele.text[category_ele.text.find('|') + 1: category_ele.text.rfind('|')].strip()
        return semester_and_year.split()[0]

    @staticmethod
    def __preprocess_career(career_ele):
        if career_ele is None:
            return ""
        return career_ele.text.strip()

    @staticmethod
    def __preprocess_major(course_ele, major_keymap: dict):
        if course_ele is None:
            return ""
        return major_keymap[course_ele.text[:course_ele.text.find(' ')].strip()]

    @staticmethod
    def __preprocess_course_num(course_ele):
        if course_ele is None:
            return ""
        return course_ele.text[course_ele.text.find(' ') + 1: course_ele.text.find('-')].strip()

    @staticmethod
    def __preprocess_course_title(course_ele):
        if course_ele is None:
            return ""
        bar_index = course_ele.text.find('-')
        return course_ele.text[course_ele.text.find(' ', bar_index + 2):].strip()

    @staticmethod
    def __preprocess_class_num(class_num_ele):
        if class_num_ele is None:
            return ""
        return class_num_ele.text.strip()

    @staticmethod
    def __preprocess_category(category_ele):
        if category_ele is None:
            return ""
        return category_ele.text[category_ele.text.rfind('|') + 2:].strip()

    @staticmethod
    def __preprocess_unit(unit_ele):
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
        if len(component_eles) is 0:
            return []
        return [c.text.strip() for c in component_eles]

    @staticmethod
    def __preprocess_professors(professor_ele):
        if professor_ele is None:
            return ""
        return [professor.strip() for professor in professor_ele.text.split(',')]

    @staticmethod
    def __preprocess_room(room_ele):
        if room_ele is None:
            return ""
        return room_ele.text.strip()

    @staticmethod
    def __preprocess_times(time_ele):
        if time_ele is None:
            return ""

        time_str = time_ele.text.strip()
        if time_str == "TBA" or time_str == "" or time_str[0].isnumeric():
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
        class_file_name: str = 'classes.txt',
        log_file_name: str = 'log.txt',
        from_major_idx: int = 56,
        to_major_idx: int = 200,
        options=None
):
    career_list = ['Undergraduate', 'Graduate', 'Non-Credit', 'Non-Degree']
    with ClassCrawler(options) as crawler:
        crawler.login("younghoonjeo", "dudgns2@")
        major_num = len(crawler.major_keymap)

        if to_major_idx > major_num:
            to_major_idx = major_num
        print(from_major_idx, "~", to_major_idx, " start")

        class_file_name = "../raw/" + '/'.join(class_file_name.split('\\'))
        log_file_name = "../raw/" + '/'.join(log_file_name.split('\\'))

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
                            class_file.write(json.dumps(info.get_info_dict(), ensure_ascii=False) + "\n")
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
