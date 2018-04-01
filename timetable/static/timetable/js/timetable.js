function LectureList(classListId) {
    var tbody = document.getElementById(classListId).getElementsByTagName("tbody")[0];
    this.lectures = [];

    this.initialize = function () {
        var i, j;
        var timeFormat = "Dd HH:MM~HH:MM";
        var rows = tbody.getElementsByTagName("tr");
        for (i = 0; i < rows.length; i++) {
            var title = rows[i].getElementsByClassName("section-title")[0].textContent;
            var professors = rows[i].getElementsByClassName("section-professors")[0].textContent;
            var message = title + "\n" + professors;
            var times = rows[i].getElementsByClassName("section-times")[0].textContent;
            var numOfTimes = times.length / timeFormat.length;
            for (j = 0; j < numOfTimes; j++) {
                var timeStr = times.substr(j * timeFormat.length, timeFormat.length);
                var dayStr = times.substr(0, 2);
                var day;
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
                var stringInfo = timeStr.substr(4);
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

            var thisStart = this.startHour * 60 + this.startMin;
            var thisEnd = this.endHour * 60 + this.endMin;
            var otherStart = other.startHour * 60 + other.startMin;
            var otherEnd = other.endHour * 60 + other.endMin;

            return thisStart <= otherStart && otherStart < thisEnd || // this < other
                otherStart <= thisStart && thisStart < otherEnd;    // other < this
        } else {
            return this.isOverlapped(makeLecture(other));
        }
    };

    this.toString = function () {
        return (startHour < 10 ? "0" : "") + startHour + ":" +
            (startMin < 10 ? "0" : "") + startMin + ":" +
            (endHour < 10 ? "0" : "") + endHour + ":" +
            (endMin < 10 ? "0" : "") + endMin + "_" +
            "day" + day;
    };

    this.getTotalMins = function () {
        return (endHour * 60 + endMin) - (startHour * 60 + startHour);
    };
}

function makeLecture(stringFormatInfo) {
    // format of info: "HH:MM~HH:MM D (any message)"
    // 'D' means 'day' which is a number representing the index of the day.
    var startHour = parseInt(stringFormatInfo.substr(0, 2));
    var startMin = parseInt(stringFormatInfo.substr(3, 2));
    var endHour = parseInt(stringFormatInfo.substr(6, 2));
    var endMin = parseInt(stringFormatInfo.substr(9, 2));
    var day = parseInt(stringFormatInfo[12]);
    var message = stringFormatInfo.substring(14);

    return new Lecture(startHour, startMin, endHour, endMin, day, message);
}

function Timetable(elementId, days, startHour, endHour) {
    var numOfDivs = 3;

    this.tableSettings = {
        divHeight: 8, // pixel
        timeWidth: 5, // percentage (0~100)
        headHeight: 20 // pixel
    };

    var table = document.getElementById(elementId);
    var theadRow = table.getElementsByTagName("thead")[0].getElementsByTagName("tr")[0];
    var tbody = table.getElementsByTagName("tbody")[0];

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
        var i;
        var lecture = makeLecture(stringInfo);
        for (i = 0; i < this.lectures.length; i++) {
            if (lecture.isSame(this.lectures[i]) || lecture.isOverlapped(this.lectures[i]))
                return false;
        }

        this.lectures.push(lecture);
        this.addRectangle(stringInfo);
        return true;
    };

    this.addRectangle = function (stringInfo) {
        var lecture = makeLecture(stringInfo);

        var divStartElement = getTimeDivElementWithStart(lecture.day, lecture.startHour, lecture.startMin);
        var divEndElement = getTimeDivElementWithEnd(lecture.day, lecture.endHour, lecture.endMin);
        var newRectangle = document.createElement("div");
        newRectangle.setAttribute("id", "lecture_" + lecture.toString());
        newRectangle.classList.add("lecture_rectangle");
        newRectangle.textContent = lecture.message;

        // width
        newRectangle.style.width = "auto";

        // height
        var top = divStartElement.getBoundingClientRect().top;
        var bottom = divEndElement.getBoundingClientRect().bottom;
        var minUnit = 30 / numOfDivs;
        newRectangle.style.height = (bottom - top) + "px";

        // css
        newRectangle.style.position = "relative";
        newRectangle.style.zIndex = "0";
        newRectangle.style.backgroundColor = "#F12345";
        newRectangle.style.textAlign = "center";
        newRectangle.style.lineHeight = newRectangle.style.height;
        newRectangle.style.verticalAlign = "middle";

        divStartElement.appendChild(newRectangle);
    };

    // TODO: adjust lecture rectangle when divHeight is changed.

    this.removeLecture = function (stringInfo) {
        for (var i = 0; i < this.lectures.length; i++) {
            if (this.lectures[i].isSame(stringInfo)) {
                this.lectures.splice(i, 1);
                this.removeRectangle(stringInfo);
                return true;
            }
        }
        return false;
    };

    this.removeRectangle = function (stringInfo) {
        var lecture = makeLecture(stringInfo);
        var rec = document.getElementById("lecture_" + lecture.toString());
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
        var i, j;

        // timeWidth
        if (this.tableSettings.timeWidth) {
            var numOfDays = table.getElementsByTagName("th").length;
            var dayWidth = (100 - this.tableSettings.timeWidth) / (numOfDays - 1);
            for (i = 1; i < numOfDays; i++) {
                var dayClassElements = table.querySelectorAll(".day" + i);
                for (j = 0; j < dayClassElements.length; j++)
                    dayClassElements[j].style.width = dayWidth + "%";
            }
        }

        // divHeight
        if (this.tableSettings.divHeight) {
            var divTimeCells = table.querySelectorAll("div.timecell");
            for (i = 0; i < divTimeCells.length; i++)
                divTimeCells[i].style.height = this.tableSettings.divHeight + "px";
        }

        // headHeight
        if (this.tableSettings.headHeight) {
            var heads = theadRow.getElementsByTagName("th");
            for (i = 0; i < heads.length; i++) {
                heads[i].style.height = this.tableSettings.headHeight + "px";
            }
        }
    };
    this.updateTableSettings();

    function setHead(days) {
        var i;
        var timeAndDays = ["Time"].concat(days);
        for (i = 0; i < timeAndDays.length; i++) {
            var dayEle = document.createElement("th");
            dayEle.setAttribute("value", i + "");
            dayEle.setAttribute("id", "day" + i);
            dayEle.classList.add("day" + i);
            dayEle.textContent = timeAndDays[i];
            theadRow.appendChild(dayEle);
        }
    }

    function setTimeRows(days, startHour, endHour) {
        var numOfRows = (endHour - startHour) * 2;
        var timeAndDays = ["Time"].concat(days);
        var i, j, k;

        for (i = 0; i < numOfRows; i++) {
            var row = document.createElement("tr");
            var timeRowStr = timeToStr(startHour + Math.floor(i / 2), i % 2 === 0 ? 0 : 30) + "~" +
                timeToStr(startHour + Math.floor((i + 1) / 2), (i + 1) % 2 === 0 ? 0 : 30);
            row.setAttribute("id", timeRowStr);
            row.classList.add(i % 2 === 0 ? "even" : "odd");

            for (j = 0; j < timeAndDays.length; j++) {
                var cell = document.createElement("td");
                cell.setAttribute("id", timeRowStr + "_day" + j);
                cell.classList.add("day" + j);

                for (k = 0; k < numOfDivs; k++) {
                    var div = document.createElement("div");

                    // set id of div
                    var divStartMin = (i % 2 === 0 ? 0 : 30) + k * 30 / numOfDivs;
                    var divStartHour = startHour + Math.floor(i / 2);

                    var divEndMin = (i % 2 === 0 ? 0 : 30) + (k + 1) * 30 / numOfDivs;
                    var divEndHour = startHour + Math.floor(i / 2);
                    if (divEndMin === 60) {
                        divEndMin = 0;
                        divEndHour += 1;
                    }

                    var timeDivStr = timeToStr(divStartHour, divStartMin) + "~"
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

            tbody.appendChild(row);
        }
    }

    function getTimeDivElementWithStart(day, startHour, startMin) {
        var minUnit = 30 / numOfDivs;

        var endMin = startMin + minUnit;
        var endHour = startHour + (endMin === 60 ? 1 : 0);
        endMin = (endMin === 60 ? 0 : endMin);
        return document.getElementById(timeToStr(startHour, startMin) + "~" + timeToStr(endHour, endMin) + "_day" + day);
    }

    function getTimeDivElementWithEnd(day, endHour, endMin) {
        var minUnit = 30 / numOfDivs;

        var startMin = endMin - minUnit;
        var startHour = endHour - (startMin < 0 ? 1 : 0);
        startMin = startMin + (startMin < 0 ? 60 : 0);
        return document.getElementById(timeToStr(startHour, startMin) + "~" + timeToStr(endHour, endMin) + "_day" + day);
    }
}

function LecturePage(classListId, timetableId, days, startHour, endHour) {
    this.lectureList = new LectureList(classListId);
    this.timetable = new Timetable(timetableId, days, startHour, endHour);

    this.initialize = function () {
        for (var i = 0; i < this.lectureList.lectures.length; i++) {
            this.timetable.addLecture(this.lectureList[i].toString());
        }
    };

    this.update = function () {
        this.lectureList.update();
        this.timetable.clearLectures();
        this.initialize();
    }
}