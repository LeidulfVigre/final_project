// Functions defined under here:
async function login(){
    try{
        const response = await fetch("login");
        console.log("Jeg blir kjørt!!");
        if(response.status !== 200) {
            console.log("An error occured during the server interraction: ", response.status);
        }
    }catch(error){
        console.error('Fetch error: ', error);
    }
}

function check_alike_password(){ 
    var password_field = document.getElementById("register_password");
    var check_password_field = document.getElementById("check_register_password");
    var password_ok = document.getElementById("password_ok"); 

    if(password_field.value === check_password_field.value){
        password_ok.innerHTML = "<p>Password ok: OK</p>";
    }else{
        password_ok.innerHTML = "<p>Password ok: Not alike</p>";
        console.log("JEG BLIR KJØRT!")
    }
    console.log("Passord field: ", password_field.value);
    console.log("re enter: ", check_password_field.value);
}

// HTML elements here
//var login_button = document.getElementById("login_button");
//login_button.onclick = login();