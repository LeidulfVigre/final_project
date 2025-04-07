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

// HTML elements here
//var login_button = document.getElementById("login_button");
//login_button.onclick = login();