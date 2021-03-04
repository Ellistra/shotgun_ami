// Function to add user input fields to the tables using the "Add Copies" button
function add_rows(){
    var row = document.getElementById("inputTable").insertRow(-1);
    var row_num =  document.getElementById("inputTable").rows.length;
    row_num--
    row.id = row_num;

    row.innerHTML =
        `
        <th>${row_num}</th>
        <td>
            <form>
                <input type="text" placeholder="link" class="link" id="new_link">
            </form>
        </td>
        <td>
            <form>
                <input type="text" placeholder="task" class="task" id="new_task">
            </form>
        </td>`;

    new_link = document.getElementById("new_link");
    new_link.name = "link"+row_num;
    new_link.id = "link"+row_num;

    new_task = document.getElementById("new_task");
    new_task.name = "task"+row_num;
    new_task.id = "task"+row_num;

    var row_no = row_num.toString();
    var message = "Created row:"+row_no;
    console.log(message);
}


function reset_input_colour(){
    table_length = document.getElementById("inputTable").rows.length;
    table_length--
    for (let  step=1; step <= table_length; step++) {
        let link = document.getElementById("link"+step);
        let task = document.getElementById("task"+step);
        link.style.backgroundColor = "";
        task.style.backgroundColor = "";
    }
    console.log("Input field colour reset.");
}


function highlight_errors(response){
    //  Parsing validation from server. Returns string of numbers of rows that failed.
    let errors = response.split("+");
    let error;
    for( error in errors ){
        //  updating style of incorrect inputs using ID
        let row_no = errors[error];
        let link = document.getElementById("link"+row_no);
        let task = document.getElementById("task"+row_no);
        link.style.backgroundColor = "LightCoral";
        task.style.backgroundColor = "LightCoral";
    }
    console.log("Validation failed, errors highlighted.");
}


function send_data(data){
    const xhr = new XMLHttpRequest();

    let urlEncodedData = "";
    let urlEncodedDataPairs = [];
    let name;
    let host = window.location.hostname;
    let host_address = "http://"+host+":5000/version/copy/validate";

    console.log("Sending to host address: "+host_address);
    for( name in data ){
        urlEncodedDataPairs.push( encodeURIComponent( name ) + '=' + encodeURIComponent( data[name] ) );
    }

    urlEncodedData = urlEncodedDataPairs.join( '&' );
    console.log("Sending data, waiting for reply.");
    xhr.open( "POST", host_address);
    xhr.setRequestHeader( 'Content-Type', 'application/x-www-form-urlencoded' );

    xhr.onload =()=>{
        let response = xhr.responseText;
        handle_validation(response);
    }

    xhr.send( urlEncodedData );
}

function handle_validation(response){
    if (response == "0"){
        document.getElementById("submit").value = "Success!";
        console.log("Validation successful, versions created in SG.");
        alert("Versions successfully created!");

    } else if (response == "ERROR_VAL") {
        alert("There was an error during validation! Please restart the AMI from Shotgun.");
        console.log("There was an error during validation.");

    } else if (response == "ERROR_CR") {
        alert("There was an error during version creation! Please check if the copies exist in shotgun before trying again.");
        console.log("There was an error during version creation.");

    } else if (response == "NO_DATA") {
        alert("No user data was entered. Please enter a shot and task.");
        console.log("There was an error during version creation.");

    } else {
        highlight_errors(response);
        document.getElementById("submit").disabled = false;
        document.getElementById("submit").value = "Resubmit";
        console.log("Form reset for resubmission.");
    }
}


function validate_data(){
    reset_input_colour();

    console.log("Beginning validation.");

    let submit_button = document.getElementById("submit");
    submit_button.disabled = true;
    submit_button.value = "Validating";

    console.log("Gathering post data.");
    let data_dict = {};

    table_length = document.getElementById("inputTable").rows.length;
    table_length--

    for (let  step=1; step <= table_length; step++) {
        let link = document.getElementById("link"+step).value;
        let task = document.getElementById("task"+step).value;

        let row_data = link+"!"+task
        data_dict[step] = row_data;
    }

    let user_id = document.getElementById("user_id").textContent;
    let project_id = document.getElementById("project_id").textContent;
    let version_id = document.getElementById("version_id").textContent;

    data_dict["user_id"] = user_id;
    data_dict["project_id"] = project_id;
    data_dict["version_id"] = version_id;

    //  Sending data to server
    send_data(data_dict);
}
