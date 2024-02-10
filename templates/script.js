function showSignup() {
    document.getElementById("signupForm").style.display = "block";
    document.getElementById("loginForm").style.display = "none";
}

function showLogin() {
    document.getElementById("signupForm").style.display = "none";
    document.getElementById("loginForm").style.display = "block";
}

function submitSignup() {
    const username = document.getElementById("signupUsername").value;
    const email = document.getElementById("signupEmail").value;
    const password = document.getElementById("signupPassword").value;
    const confirm_password = document.getElementById("signupConfirmPassword").value;
    const country_code = document.getElementById("signupCountryCode").value;
    const phone_number = document.getElementById("signupPhoneNumber").value;

    const data = {
        username: username,
        email: email,
        password: password,
        confirm_password: confirm_password,
        country_code: country_code,
        phone_number: phone_number
    };

    fetch('https://12f7-2605-a601-559b-1800-2845-dd74-d44b-476b.ngrok-free.app/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(responseData => {
        console.log('Signup Response:', responseData);

        // Handle the response as needed (e.g., display a success message or redirect)
    })
    .catch(error => {
        console.error('Error during signup:', error);
        // Handle errors (e.g., display an error message to the user)
    });
}

function submitLogin() {
    const username = document.getElementById("loginUsername").value;
    const password = document.getElementById("loginPassword").value;

    const data = {
        username: username,
        password: password
    };

    fetch('https://12f7-2605-a601-559b-1800-2845-dd74-d44b-476b.ngrok-free.app/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(responseData => {
        console.log('Login Response:', responseData);

        // Handle the response as needed (e.g., display a success message or redirect)
    })
    .catch(error => {
        console.error('Error during login:', error);
        // Handle errors (e.g., display an error message to the user)
    });
}

