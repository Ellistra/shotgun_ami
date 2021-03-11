// Function to add user input fields to the tables using the "Add Copies" button
function add_rows(){
    // Creating new table row and assigning it a number ID
    var row = document.getElementById("inputTable").insertRow(-1);
    var row_num = document.getElementById("inputTable").rows.length;
    row_num--
    row.id = row_num;

    // Adding html to row with default IDs
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

    // Getting newly created row and giving bespoke ids to input fields
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

// Function to reset the user input fields to default colour.
function reset_input_colour(){
    // Get user inpit table, go through rows and reset style.
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

// Function to highlight incorrect user input cells pink after validation.
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

// Function to send user input data back to the server for validation.
function send_data(data){
    const xhr = new XMLHttpRequest();

    // URL encoding user input data for transfer.
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

    // Opening post request back to sever
    console.log("Sending data, waiting for reply.");
    xhr.open( "POST", host_address);
    xhr.setRequestHeader( 'Content-Type', 'application/x-www-form-urlencoded' );

    // Wait for a response, then send it to a handler function.
    xhr.onload =()=>{
        let response = xhr.responseText;
        handle_validation(response);
    }

    // Sending Post.
    xhr.send( urlEncodedData );
}

// Function to handle response code from server.
function handle_validation(response){
    // If successful, alert user, leave submit button deactivated.
    if (response == "0"){
        document.getElementById("submit").value = "Success!";
        console.log("Validation successful, versions created in SG.");
        alert("Versions successfully created!");
    // If unknown error during validation, alert user.
    } else if (response == "ERROR_CR") {
        alert("There was an unknown error during version creation! Please check if the copies exist in shotgun before trying again.");
        console.log("There was an error during version creation.");
    // If error during batch of versions, alert user.
    } else if (response == "ERROR_BATCH") {
        alert("There was an error while trying to batch create versions in Shotgun. This may be due to the website being down. Please try again later.");
        console.log("There was an error during version creation.");
    // If error during upload of attachments, alert user.
    } else if (response == "ERROR_ATT") {
        alert("There was an error while trying to upload version media. New versions have been created but may be missing their uploaded movie.");
        console.log("There was an error during version creation.");
    // If no user input data recieved, alert user.
    } else if (response == "NO_DATA") {
        alert("No user data was entered. Please enter a shot and task.");
        console.log("There was an error during version creation.");
    // If errors are recieved, re-enable the submit button and highlight errors.
    } else {
        highlight_errors(response);
        document.getElementById("submit").disabled = false;
        document.getElementById("submit").value = "Resubmit";
        console.log("Form reset for resubmission.");
    }
}

// Function activated when Submit button clicked.
function validate_data(){
    // Resetting user input cell colour to default.
    reset_input_colour();

    // Disabling Submit button.
    console.log("Beginning validation.");
    let submit_button = document.getElementById("submit");
    submit_button.disabled = true;
    submit_button.value = "Validating";

    console.log("Gathering post data.");
    let data_dict = {};

    // Getting user input table length
    table_length = document.getElementById("inputTable").rows.length;
    table_length--

    // Cycling through each row in user input table and adding data to dict.
    for (let  step=1; step <= table_length; step++) {
        let link = document.getElementById("link"+step).value;
        let task = document.getElementById("task"+step).value;

        let row_data = link+"!"+task
        data_dict[step] = row_data;
    }

    // Getting other important data to send back to the server.
    let user_id = document.getElementById("user_id").textContent;
    data_dict["user_id"] = user_id;
    let project_id = document.getElementById("project_id").textContent;
    data_dict["project_id"] = project_id;
    let version_id = document.getElementById("version_id").textContent;
    data_dict["version_id"] = version_id;

    //  Sending data
    send_data(data_dict);
}
