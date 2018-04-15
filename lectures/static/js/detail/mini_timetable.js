function MiniTimetable(startHour, endHour, pxPerHour) {
    this.table = null;
    this.sections = [];
    this.tempSection = null;

    this.newTimetable = function () {
        let segment = document.getElementById('timetable_segment');
        this.table = document.createElement('table');
        let thead = document.createElement('thead');
        let trForHead = document.createElement('tr');
        thead.appendChild(trForHead);
        table.appendChild(thead);
        segment.appendChild(table);

        // table head
        for (let i = 0; i < 7; i++) {
            let th = document.createElement('th');
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
            switch (i) {
                case 0:
                    td.setAttribute('id', 'timetable_Mo');
                    break;
                case 1:
                    td.setAttribute('id', 'timetable_Tu');
                    break;
                case 2:
                    td.setAttribute('id', 'timetable_We');
                    break;
                case 3:
                    td.setAttribute('id', 'timetable_Th');
                    break;
                case 4:
                    td.setAttribute('id', 'timetable_Fr');
                    break;
                case 5:
                    td.setAttribute('id', 'timetable_Sa');
                    break;
                default:
                    td.setAttribute('id', 'timetable_Su');
            }
            td.style.height = ((endHour - startHour) * pxPerHour) + 'px';
            td.classList.add('timetable-column');
            tr.appendChild(td);
        }
    };

    this.addSections = function (sections) {
        for (let i = 0; i < sections.length; i++) {
            let sectionData = new SectionData(sections[i], startHour, pxPerHour);
            for (let j = 0; j < sections[i].times.length; j++) {
                document.getElementById('timetable_' + sections[i].day).appendChild(sectionData.elements[j]);
            }
            this.sections.push(sectionData);
        }
    };

    this.addTemporarySection = function (tempSection) {
        let sectionData = new SectionData(tempSection, startHour, pxPerHour);
        for (let j = 0; j < tempSection.times.length; j++) {
            document.getElementById('timetable_' + tempSection.day).appendChild(sectionData.elements[j]);
        }
        this.tempSection = sectionData;
    };

    this.deleteTimetable = function () {
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
    };
}

function SectionData(section, startHour, pxPerHour) {
    this.section = section;
    this.elements = [];

    for (let i = 0; i < section.times[i]; i++) {
        let element = document.createElement('div');
        element.style.width = '100%';
        element.style.height = (((section.times[i].endHour - section.times[i].startHour)
            + (section.times[i].endMin - section.times[i].startMin) / 60.0) * pxPerHour) + 'px';
        element.style.top = (((section.times[i].startHour - startHour)
            + section.times[i].startMin / 60.0) * pxPerHour) + 'px';
        element.style.backgroundColor = '#1234FF';
        this.elements.push(element);
    }
}