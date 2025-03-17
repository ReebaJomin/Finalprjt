function goToInfoPage() {
    document.getElementById("home").classList.add("hidden");
    document.getElementById("user-info").classList.remove("hidden");
}

// Function to handle login
function loginUser() {
    let username = document.getElementById("name").value;
    let gender = document.getElementById("gender").value;

    if (!username || !gender) {
        
        return;
    }

    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, gender })
    })
    .then(response => response.json())
    .then(data => {
        if (data.user_id) {
            console.log("Login Successful. User ID:", data.user_id);
            let storedUser = localStorage.getItem('user_id');
            if (storedUser && storedUser !== data.user_id) {
                localStorage.clear();  // Reset all stored data
            }
            localStorage.setItem("user_id", data.user_id);
            localStorage.setItem("username", username);
            localStorage.setItem("userGender", gender);
            window.location.href = "dashboard.html"; // Redirect after setting storage
 // Redirect to roadmap page
        } else {
            alert("Sign Up first.");
        }
    })
    .catch(error => console.error("Error logging in:", error));
}

// Function to handle signup
function signupUser() {
    let username = document.getElementById("name").value;
    let gender = document.getElementById("gender").value;

    if (!username || !gender) {
        
        return;
    }

    fetch("/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, gender })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.message === "Signup successful!") {
            let storedUser = localStorage.getItem('user_id');
            localStorage.setItem("user_id", data.user_id);
            if (storedUser && storedUser !== data.user_id) {
                localStorage.clear();  // Reset all stored data
            }
            localStorage.setItem("username", username);
            localStorage.setItem("userGender", gender);
            window.location.href = "dashboard.html"; // Redirect after setting storage

        }
    })
    .catch(error => console.error("Error signing up:", error));
}
document.addEventListener("DOMContentLoaded", loginUser);
document.addEventListener("DOMContentLoaded", signupUser);