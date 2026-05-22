const passwordInput =
document.getElementById(
    "password"
);

const showPassword =
document.getElementById(
    "showPassword"
);

// SHOW PASSWORD

showPassword.addEventListener(
    "change",
    () => {

        if(showPassword.checked){

            passwordInput.type =
            "text";

        }

        else{

            passwordInput.type =
            "password";

        }

    }
);