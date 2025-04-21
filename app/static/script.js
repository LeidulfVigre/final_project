// Functions defined under here:

const search_bar = document.getElementById("search_bar");
search_bar.addEventListener("blur", () => {
    const search_results = document.getElementById("search_results");
    search_results.innerHTML = "";
})

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

async function handle_sorting(username){
    const choose_review_rating = document.getElementById("choose_review_rating").value;
    const order_by_date = document.getElementById("order_by_date").value;
    const order_by_score = document.getElementById("order_by_score").value;
    const select_genre = document.getElementById("select_genre").value;


    
    try{
        let url = "/handle_sorting?username="+ username +"&choose_review_rating="+choose_review_rating+"&order_by_date="+order_by_date+"&order_by_score="+order_by_score+"&select_genre="+select_genre;
        const response = await fetch(url);
        if (response.status !== 200) {
            console.log("Problem getting data from server: ", response.status);
        }else{
            let content_bottom = document.getElementById("content_bottom");
            
            const html = await response.text()
            content_bottom.innerHTML = html;
        }
    }catch(error){
        console.log("Problem connecting to server: ", error);
    }
}

async function search_for_movie(){
    const search_results = document.getElementById("search_results");
    const search_bar     = document.getElementById("seach_bar");
    movie_name = search_bar.value;

    try{
        let url = "/search?movie_name=" + movie_name;
        const response = await fetch(url);
        if (response.status !== 200){
            console.log("Problem getting data from server: ", response.status);
        }else{
            const html = await response.text()
            search_results.innerHTML = html;
        }
    }catch(error){
        console.log("Problem connecting to server: ", error);
    }
}

async function change_button_to_dropdown(movie_id){
    button_area = document.getElementById("button_area");
    write_review_button = document.getElementById("write_review_button");
    rating_button = document.getElementById("rating_button");

    button_area.removeChild(rating_button);
    
    const dropdown_menu = document.createElement("select");
    dropdown_menu.id = "dropdown_menu";

    for(var i; i < 6; i++){
        let option = document.createElement("option");
        option.textContent = ""+(i+1);
        option.value = ""+(i+1);
        dropdown.appendChild(option);
    }

    dropdown_menu.addEventListener("change", async function (){
        try{
            let value = this.value;
            let url = "/rate_movie"

            const response = await fetch(url,{
                method:"POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({selected_value:value, movie:movie_id})
            });

            if(response !== 200){
                console.log("Problem sending data to server: ", response.status);
            }else{
                const button_area = document.getElementById("button_area");
                const dropdown_menu = document.getElementById("dropdown_menu");
                const validation_text = document.createElement("p");
                
                validation_text.textContent = "Movie Rated"
                button_area.removeChild(dropdown_menu);
                button_area.appendChild(validation_text);
            }
        }catch(error){
            console.log("Problem connecting to server: ", error);
        }   
    })

    button_area.appendChild(dropdown_menu);
}

async function delete_review(review_id){
    try{
        let url = "/delete_review";
        const response = await fetch(url, {
            method:"POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({selected_review:review_id})
        });
    }catch(error){
        console.log("Problem connecting to server: ", error);
    }
}

async function delete_user(){
    try{
        let url = "/delete_user";
        const response = await fetch(url, {
            method:"POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({sent_data:"junk data"})
        });
    }catch(error){
        console.log("Problem connecting to server: ", error);
    }
}

// HTML elements here
//var login_button = document.getElementById("login_button");
//login_button.onclick = login();