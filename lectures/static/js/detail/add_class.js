function findClickedButton(timetable_input_class_name) {
    let inputs = document.getElementsByClassName(timetable_input_class_name);
    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].checked) {
            let input_id = inputs[i].getAttribute('id');
            return input_id.substr(input_id.lastIndexOf('_') + 1,);
        }
    }
    return 'null';
}