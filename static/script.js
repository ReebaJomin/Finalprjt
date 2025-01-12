// Function to go to the user info page
function goToInfoPage() {
    document.getElementById('home').classList.add('hidden');
    document.getElementById('user-info').classList.remove('hidden');
}

// Function to go to the learning roadmap
function submitForm(event) {
    event.preventDefault();
    
    // Get values from form
    let name = document.getElementById('name').value;
    let gender = document.getElementById('gender').value;

    if (name && gender) {
        // Save data to localStorage
        localStorage.setItem('userName', name);
        localStorage.setItem('userGender', gender);

        // Redirect to roadmap page
        window.location.href = 'roadmap.html';
    } else {
        alert('Please enter all details');
    }
}


// Dummy user progress
let userProgress = 1; // Example: user has completed Level 1

// Function to update levels based on progress
function updateLevels() {
    if (userProgress >= 1) {
        document.getElementById('level2').classList.remove('locked');
    }
    if (userProgress >= 2) {
        document.getElementById('level3').classList.remove('locked');
    }
}

// Call updateLevels on page load
document.addEventListener('DOMContentLoaded', updateLevels);