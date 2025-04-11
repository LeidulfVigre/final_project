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
    var submit_registration = document.getElementById("submit_registration");

    if(password_field.value === check_password_field.value){
        password_ok.innerHTML = "<p>Password ok: OK</p>";
        submit_registration.disabled = false;
    }else{
        password_ok.innerHTML = "<p>Password ok: Not alike</p>";
        submit_registration.disabled = true;
    }
}

/* 
OBS MÅ LEGGE PÅ EVENT LISTENERS!!!! DA KAN JEG ENKELT SJEKKE NÅVÆRENDE VERDIER FOR HVERT VALG OG SÅ SENDE DETTE TIL SERVEREN
SERVEREN VIL DA BYGGE QUERIET UT I FRA HVILKE VALG SOM ER TATT!!!!!!!!!!!
*/

async function handle_sorting(username){
    

    try{
        let url = "/login?username="+ username +"&choice="+value;
        const response = await fetch(url);
        if (response.status !== 200) {
            console.log("Problem getting data from server: ", response.status);
        }else{
            let content_bottom = document.getElementById("content_bottom");
            
            

        }
    }catch(error){
        console.log("Problem connecting to server: ", error);
    }
}


// HTML elements here
//var login_button = document.getElementById("login_button");
//login_button.onclick = login();