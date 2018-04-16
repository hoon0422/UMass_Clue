function MiniTimetable(startHour, endHour, pxPerHour) {
    this.table = null;
    this.sections = [];
    this.tempSection = null;

    this.newTimetable = function () {
        let segment = document.getElementById('timetable_segment');
        this.table = document.createElement('table');
        this.table.style.borderCollapse = "collapse";
        this.table.style.border = "1px solid black";
        let thead = document.createElement('thead');
        let trForHead = document.createElement('tr');
        thead.appendChild(trForHead);
        this.table.appendChild(thead);
        segment.appendChild(this.table);

        // table head
        for (let i = 0; i < 7; i++) {
            let th = document.createElement('th');
            th.style.border = "1px solid black";
            switch (i) {
                case 0:
                    th.textContent = 'Mo';
                    break;
                case 1:
                    th.textContent = 'Tu';
                    break;
                case 2:
                    th.textContent = 'We';
                    break;
                case 3:
                    th.textContent = 'Th';
                    break;
                case 4:
                    th.textContent = 'Fr';
                    break;
                case 5:
                    th.textContent = 'Sa';
                    break;
                default:
                    th.textContent = 'Su';
            }
            th.style.textAlign = 'center';
            th.style.padding = '5px';
            trForHead.appendChild(th);
        }

        // table row
        let tr = document.createElement('tr');
        for (let i = 0; i < 7; i++) {
            let td = document.createElement('td');
            td.style.border = "1px solid black";
            let columnDiv = document.createElement('div');
            columnDiv.style.width = '100%';
            columnDiv.style.position = 'relative';
            td.appendChild(columnDiv);
            switch (i) {
                case 0:
                    columnDiv.setAttribute('id', 'timetable_Mo');
                    break;
                case 1:
                    columnDiv.setAttribute('id', 'timetable_Tu');
                    break;
                case 2:
                    columnDiv.setAttribute('id', 'timetable_We');
                    break;
                case 3:
                    columnDiv.setAttribute('id', 'timetable_Th');
                    break;
                case 4:
                    columnDiv.setAttribute('id', 'timetable_Fr');
                    break;
                case 5:
                    columnDiv.setAttribute('id', 'timetable_Sa');
                    break;
                default:
                    columnDiv.setAttribute('id', 'timetable_Su');
            }
            columnDiv.style.height = ((endHour - startHour) * pxPerHour) + 'px';
            columnDiv.classList.add('timetable-column');
            tr.appendChild(td);
            let tbody = document.createElement('tbody');
            tbody.appendChild(tr);
            this.table.appendChild(tbody);
        }
    };

    this.addSections = function (sections) {
        for (let i = 0; i < sections.length; i++) {
            let sectionData = new SectionData(sections[i], startHour, pxPerHour);
            for (let j = 0; j < sections[i].times.length; j++) {
                document.getElementById('timetable_' + sections[i].times[j].day).appendChild(sectionData.elements[j]);
            }
            this.sections.push(sectionData);
        }
    };

    this.addTemporarySection = function (tempSection) {
        let sectionData = new SectionData(tempSection, startHour, pxPerHour, '#11FF11', 0.4);
        for (let i = 0; i < tempSection.times.length; i++) {
            document.getElementById('timetable_' + tempSection.times[i].day).appendChild(sectionData.elements[i]);
        }
        this.tempSection = sectionData;
    };

    this.deleteTimetable = function () {
        if (this.table !== null) {
            for (let i = 0; i < this.sections.length; i++) {
                for (let j = 0; j < this.sections[i].elements.length; j++) {
                    this.sections[i].elements[j].remove();
                }
            }
            this.sections = [];

            for (let i = 0; i < this.tempSection.elements.length; i++) {
                this.tempSection.elements[i].remove();
            }
            this.tempSection = null;

            this.table.remove();
            this.table = null;
        }
    };
}

function SectionData(section, startHour, pxPerHour, color, opacity) {
    this.section = section;
    this.elements = [];

    for (let i = 0; i < section.times.length; i++) {
        let element = document.createElement('div');
        element.style.position = 'absolute';
        element.style.width = '100%';
        element.style.height = (((section.times[i].endHour - section.times[i].startHour)
            + (section.times[i].endMin - section.times[i].startMin) / 60.0) * pxPerHour) + 'px';
        element.style.top = (((section.times[i].startHour - startHour)
            + section.times[i].startMin / 60.0) * pxPerHour) + 'px';
        element.style.backgroundColor = color ? color : '#1234FF';
        if (opacity) {
            element.style.filter = "alpha(opacity=" + opacity + ")";
            element.style.opacity = opacity;
        }
        this.elements.push(element);
    }
}