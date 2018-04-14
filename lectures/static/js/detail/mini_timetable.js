function MiniTimetable(sections) {
    this.pxPerHour = null;
    this.startHour = null;
    this.endHour = null;


    this.newTimetable = function (startHour, endHour, pxPerHour) {
        this.pxPerHour = pxPerHour;
        this.startHour = startHour;
        this.endHour = endHour;

        let segment = document.getElementById('timetable_segment');
        let table = document.createElement('table');
        let thead = document.createElement('thead');
        let trForHead = document.createElement('tr');
        thead.appendChild(trForHead);
        table.appendChild(thead);
        segment.appendChild(table);

        // table head
        for (let i = 0; i < 7; i++) {
            let th = document.createElement('th');
            switch(i) {
                case 0: th.textContent = 'Mo'; break;
                case 1: th.textContent = 'Tu'; break;
                case 2: th.textContent = 'We'; break;
                case 3: th.textContent = 'Th'; break;
                case 4: th.textContent = 'Fr'; break;
                case 5: th.textContent = 'Sa'; break;
                default: th.textContent = 'Su';
            }
            th.style.textAlign = 'center';
            th.style.padding = '5px';
            trForHead.appendChild(th);
        }

        // table row
        let tr = document.createElement('tr');
        for (let i = 0; i < 7; i++) {
            let td = document.createElement('td');
            switch(i) {
                case 0: td.setAttribute('id', 'timetable_Mo'); break;
                case 1: td.setAttribute('id', 'timetable_Tu'); break;
                case 2: td.setAttribute('id', 'timetable_We'); break;
                case 3: td.setAttribute('id', 'timetable_Th'); break;
                case 4: td.setAttribute('id', 'timetable_Fr'); break;
                case 5: td.setAttribute('id', 'timetable_Sa'); break;
                default: td.setAttribute('id', 'timetable_Su');
            }
            td.style.height = ((endHour - startHour) * pxPerHour) + 'px';
            td.classList.add('timetable-column');
            tr.appendChild(td);
        }
    };


}