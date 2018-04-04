function LectureList(classListId) {
    const tbody = document.getElementById(classListId).getElementsByTagName("tbody")[0];
    this.lectures = [];

    function timeStrToTimes(timeStr, token) {
        const times = timeStr.split(token);
        let i;
        for (i = 0; i < times.length; i++)
            times[i] = times[i].trim();

        while ((i = times.indexOf("")) !== -1) {
            times.splice(i, 1);
        }
        while ((i = times.indexOf("\n")) !== -1) {
            times.splice(i, 1);
        }
        return times;
    }

    this.initialize = function () {
        let i, j;
        const timeFormat = "Dd HH:MM~HH:MM";
        const rows = tbody.getElementsByTagName("tr");
        for (i = 0; i < rows.length; i++) {
            const title = rows[i].getElementsByClassName("section-title")[0].textContent.trim();
            const professors = rows[i].getElementsByClassName("section-professors")[0].textContent.trim();
            const message = title + "\n" + professors;
            const timeStr = rows[i].getElementsByClassName("section-times")[0].textContent.trim();
            const times = timeStrToTimes(timeStr, "  ");
            for (j = 0; j < times.length; j++) {
                const dayStr = times[j].substr(0, 2);
                let day;
                switch (dayStr) {
                    case "Mo":
                        day = 1;
                        break;
                    case "Tu":
                        day = 2;
                        break;
                    case "We":
                        day = 3;
                        break;
                    case "Th":
                        day = 4;
                        break;
                    case "Fr":
                        day = 5;
                        break;
                    case "Sa":
                        day = 6;
                        break;
                    default:
                        day = 7;
                        break;
                }
                let stringInfo = times[j].substr(3);
                stringInfo += "_day" + day + " " + message;
                this.lectures.push(makeLecture(stringInfo));
            }
        }
    };
    this.initialize();

    this.update = function () {
        this.lectures.clear();
        this.initialize();
    }
}

function timeToStr(hour, min) {
    return (hour < 10 ? "0" : "") + hour + ":" + (min < 10 ? "0" : "") + min;
}

function Lecture(startHour, startMin, endHour, endMin, day, message) {
    this.startHour = startHour;
    this.startMin = startMin;
    this.endHour = endHour;
    this.endMin = endMin;
    this.day = day;
    this.message = message;

    this.isSame = function (other) {
        if (other instanceof Lecture) {
            return this.startHour === other.startHour &&
                this.startMin === other.startMin &&
                this.endHour === other.endHour &&
                this.endMin === other.endMin &&
                this.day === other.day;
        } else {
            return this.isSame(makeLecture(other));
        }
    };

    this.isOverlapped = function (other) {
        if (other instanceof Lecture) {
            if (this.day !== other.day)
                return false;

            const thisStart = this.startHour * 60 + this.startMin;
            const thisEnd = this.endHour * 60 + this.endMin;
            const otherStart = other.startHour * 60 + other.startMin;
            const otherEnd = other.endHour * 60 + other.endMin;

            return thisStart <= otherStart && otherStart < thisEnd || // this < other
                otherStart <= thisStart && thisStart < otherEnd;    // other < this
        } else {
            return this.isOverlapped(makeLecture(other));
        }
    };

    this.toString = function () {
        return (startHour < 10 ? "0" : "") + startHour + ":" +
            (startMin < 10 ? "0" : "") + startMin + "~" +
            (endHour < 10 ? "0" : "") + endHour + ":" +
            (endMin < 10 ? "0" : "") + endMin + "_" +
            "day" + day + " " +
            message;
    };

    this.getTotalMins = function () {
        return (endHour * 60 + endMin) - (startHour * 60 + startHour);
    };
}

function makeLecture(stringFormatInfo) {
    // format of info: "HH:MM~HH:MM_dayD (any message)"
    // 'D' means 'day' which is a number representing the index of the day.
    const startHour = parseInt(stringFormatInfo.substr(0, 2));
    const startMin = parseInt(stringFormatInfo.substr(3, 2));
    const endHour = parseInt(stringFormatInfo.substr(6, 2));
    const endMin = parseInt(stringFormatInfo.substr(9, 2));
    const day = parseInt(stringFormatInfo[15]);
    const message = stringFormatInfo.substring(17);
    return new Lecture(startHour, startMin, endHour, endMin, day, message);
}

function Timetable(elementId, days, startHour, endHour) {
    const numOfDivs = 6;

    this.tableSettings = {
        divHeight: 8, // pixel
        timeWidth: 5, // percentage (0~100)
        headHeight: 20 // pixel
    };

    const table = document.getElementById(elementId);
    const theadRow = table.getElementsByTagName("thead")[0].getElementsByTagName("tr")[0];
    const tbody = table.getElementsByTagName("tbody")[0];

    this.days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];
    if (days !== undefined) this.days = days;

    this.startHour = 6;
    if (startHour !== undefined) this.startHour = startHour;

    this.endHour = 20;
    if (endHour !== undefined) this.endHour = endHour;

    this.lectures = [];

    setHead(this.days);
    setTimeRows(this.days, this.startHour, this.endHour);

    this.addLecture = function (stringInfo) {
        let i;
        const lecture = makeLecture(stringInfo);
        for (i = 0; i < this.lectures.length; i++) {
            if (lecture.isSame(this.lectures[i]) || lecture.isOverlapped(this.lectures[i]))
                return false;
        }

        this.lectures.push(lecture);
        this.addRectangle(stringInfo);
        return true;
    };

    this.addRectangle = function (stringInfo) {
        const lecture = makeLecture(stringInfo);
        const divStartElement = getTimeDivElementWithStart(lecture.day, lecture.startHour, lecture.startMin);
        const divEndElement = getTimeDivElementWithEnd(lecture.day, lecture.endHour, lecture.endMin);
        const newRectangle = document.createElement("div");
        const info = document.createElement('div');
        const title = document.createElement('p');
        const professors = document.createElement('p');
        newRectangle.setAttribute("id", "lecture_" + lecture.toString());
        newRectangle.classList.add("lecture_rectangle");
        newRectangle.appendChild(info);

        let titleMessage, professorsMessage;
        let temp = lecture.message.split('\n');
        titleMessage = temp[0];
        professorsMessage = temp[1];

        info.setAttribute("id", "info_" + lecture.toString());
        info.classList.add("lecture_rectangle-info");
        title.setAttribute("id", "title_" + lecture.toString());
        title.classList.add("lecture_rectangle-info-title");
        professors.setAttribute("id", "professors_" + lecture.toString());
        professors.classList.add("lecture_rectangle-info-professors");
        title.textContent = titleMessage;
        professors.textContent = professorsMessage;
        info.appendChild(title);
        info.appendChild(professors);

        // height
        const top = divStartElement.getBoundingClientRect().top;
        const bottom = divEndElement.getBoundingClientRect().bottom;
        const minUnit = 30 / numOfDivs;
        newRectangle.style.height = (bottom - top) + "px";

        // color
        newRectangle.style.backgroundColor = "#F12345";

        divStartElement.appendChild(newRectangle);
    };

    // TODO: adjust lecture rectangle when divHeight is changed.

    this.removeLecture = function (stringInfo) {
        for (let i = 0; i < this.lectures.length; i++) {
            if (this.lectures[i].isSame(stringInfo)) {
                this.lectures.splice(i, 1);
                this.removeRectangle(stringInfo);
                return true;
            }
        }
        return false;
    };

    this.removeRectangle = function (stringInfo) {
        const lecture = makeLecture(stringInfo);
        const rec = document.getElementById("lecture_" + lecture.toString());
        if (rec) {
            rec.remove();
        }
    };

    this.clearLectures = function () {
        while (this.lectures.length !== 0) {
            this.removeRectangle(this.lectures.pop().toString());
        }
    };

    this.updateTableSettings = function () {
        let i, j;

        // timeWidth
        if (this.tableSettings.timeWidth) {
            const numOfDays = table.getElementsByTagName("th").length;
            const dayWidth = (100 - this.tableSettings.timeWidth) / (numOfDays - 1);
            for (i = 1; i < numOfDays; i++) {
                const dayClassElements = table.querySelectorAll(".day" + i);
                for (j = 0; j < dayClassElements.length; j++)
                    dayClassElements[j].style.width = dayWidth + "%";
            }
            const timeClassElements = table.querySelectorAll(".day0");
            for (i = 0; i < timeClassElements.length; i++) {
                timeClassElements[i].style.width = this.tableSettings.timeWidth + "%";
            }
        }

        // divHeight
        if (this.tableSettings.divHeight) {
            const divTimeCells = table.querySelectorAll("div.timecell");
            for (i = 0; i < divTimeCells.length; i++)
                divTimeCells[i].style.height = this.tableSettings.divHeight + "px";
        }

        // headHeight
        if (this.tableSettings.headHeight) {
            const heads = theadRow.getElementsByTagName("th");
            for (i = 0; i < heads.length; i++) {
                heads[i].style.height = this.tableSettings.headHeight + "px";
            }
        }
    };
    this.updateTableSettings();

    function setHead(days) {
        let i;
        const timeAndDays = ["Time"].concat(days);
        for (i = 0; i < timeAndDays.length; i++) {
            const dayEle = document.createElement("th");
            dayEle.setAttribute("value", i + "");
            dayEle.setAttribute("id", "day" + i);
            dayEle.classList.add("day" + i);
            dayEle.textContent = timeAndDays[i];
            theadRow.appendChild(dayEle);
        }
    }

    function setTimeRows(days, startHour, endHour) {
        const numOfRows = (endHour - startHour) * 2;
        const timeAndDays = ["Time"].concat(days);
        let i, j, k;

        for (i = 0; i < numOfRows; i++) {
            const row = document.createElement("tr");
            const timeRowStr = timeToStr(startHour + Math.floor(i / 2), i % 2 === 0 ? 0 : 30) + "~" +
                timeToStr(startHour + Math.floor((i + 1) / 2), (i + 1) % 2 === 0 ? 0 : 30);
            row.setAttribute("id", timeRowStr);
            row.classList.add(i % 2 === 0 ? "even" : "odd");

            for (j = 0; j < timeAndDays.length; j++) {
                const cell = document.createElement("td");
                cell.setAttribute("id", timeRowStr + "_day" + j);
                cell.classList.add("day" + j);

                for (k = 0; k < numOfDivs; k++) {
                    const div = document.createElement("div");

                    // set id of div
                    const divStartMin = (i % 2 === 0 ? 0 : 30) + k * 30 / numOfDivs;
                    const divStartHour = startHour + Math.floor(i / 2);

                    let divEndMin = (i % 2 === 0 ? 0 : 30) + (k + 1) * 30 / numOfDivs;
                    let divEndHour = startHour + Math.floor(i / 2);
                    if (divEndMin === 60) {
                        divEndMin = 0;
                        divEndHour += 1;
                    }

                    const timeDivStr = timeToStr(divStartHour, divStartMin) + "~"
                        + timeToStr(divEndHour, divEndMin) + "_day" + j;
                    div.setAttribute("id", timeDivStr);

                    // set class of div
                    div.classList.add("timecell");

                    // set text (for test)
                    // div.textContent = "----";

                    cell.appendChild(div);
                }

                row.appendChild(cell);
            }

            let firstTimeDiv = row.getElementsByClassName("day0")[0];
            firstTimeDiv.textContent = timeToStr(startHour + Math.floor(i / 2), i % 2 === 0 ? 0 : 30);

            tbody.appendChild(row);
        }
    }

    function getTimeDivElementWithStart(day, startHour, startMin) {
        const minUnit = 30 / numOfDivs;

        let endMin = startMin + minUnit;
        const endHour = startHour + (endMin === 60 ? 1 : 0);
        endMin = (endMin === 60 ? 0 : endMin);
        return document.getElementById(timeToStr(startHour, startMin) + "~" + timeToStr(endHour, endMin) + "_day" + day);
    }

    function getTimeDivElementWithEnd(day, endHour, endMin) {
        const minUnit = 30 / numOfDivs;

        let startMin = endMin - minUnit;
        const startHour = endHour - (startMin < 0 ? 1 : 0);
        startMin = startMin + (startMin < 0 ? 60 : 0);
        return document.getElementById(timeToStr(startHour, startMin) + "~" + timeToStr(endHour, endMin) + "_day" + day);
    }
}

function LecturePage(classListId, timetableId, days, startHour, endHour) {
    this.lectureList = new LectureList(classListId);
    this.timetable = new Timetable(timetableId, days, startHour, endHour);

    this.initialize = function () {
        for (let i = 0; i < this.lectureList.lectures.length; i++) {
            this.timetable.addLecture(this.lectureList.lectures[i].toString());
        }
    };
    this.initialize();

    this.update = function () {
        this.lectureList.update();
        this.timetable.clearLectures();
        this.initialize();
    }
}