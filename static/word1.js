let currentQuestionIndex = 0;
let correctAnswers = 0;
let incorrectQuestions = [];
let answeredQuestions = [];
let totalQuestions = 0;
let initialTotalQuestions = 0; // New variable to store the original total number of questions

let wordData = [
    {word:'After'},
{ word: 'Cannot'},
{ word: 'Good'},
{ word: 'Again'},
{ word: 'Change'},
{ word: 'Great'},
{ word: 'Against'},
{ word: 'College'},
{ word: 'Hand'},
{ word: 'Age'},
{ word: 'Come'},
{ word: 'Hands'},
{ word: 'All'},
{ word: 'Computer'},
{ word: 'Happy'},
{ word: 'Alone'},
{ word: 'Day'},
{ word: 'Hello'},
{ word: 'Also'},
{ word: 'Distance'},
{ word: 'Help'},
{ word: 'And'},
{ word: 'Do Not'},
{ word: 'Her'},
{ word: 'Ask'},
{ word: 'Do'},
{ word: 'Here'},
{ word: 'At'},
{ word: 'Does Not'},
{ word: 'His'},
{ word: 'Be'},
{ word: 'Eat'},
{ word: 'Home'},
{ word: 'Beautiful'},
{ word: 'Engineer'},
{ word: 'Homepage'},
{ word: 'Before'},
{ word: 'Fight'},
{ word: 'How'},
{ word: 'Best'},
{ word: 'Finish'},
{ word: 'Invent'},
{ word: 'Better'},
{ word: 'From'},
{ word: 'It'},
{ word: 'Busy'},
{ word: 'Glitter'},
{ word: 'But' },
    { word: 'Go' },
    { word: 'Keep' },
    { word: 'Language' },
    { word: 'Bye' },
    { word: 'God' },
    { word: 'Laugh'},
    { word: 'Can'},
    { word: 'Gold'},
    { word: 'Learn'}
];

// Shuffle function for randomizing questions
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

// Update progress bar after each correct answer
function updateProgressBar(forceComplete = false) {
    const progressBar = document.getElementById('quiz-progress');
    const progressText = document.getElementById('progress-text');

    // Calculate progress percentage
    const progressPercentage = forceComplete
        ? 100
        : (correctAnswers / initialTotalQuestions) * 100;

    progressBar.value = progressPercentage;
    progressText.textContent = `${Math.round(progressPercentage)}% completed`;
}

function checkQuizCompletion() {
    let passingScore = 100; // Example: 80% required to pass
    let progressPercentage = (correctAnswers / initialTotalQuestions) * 100;
    if (correctAnswers === initialTotalQuestions) {
        progressPercentage = 100;
    }
    localStorage.setItem("noquiz", progressPercentage);
    if (progressPercentage >= passingScore) {
        /*fetch("/get_current_user")
        .then(response => response.json())
        .then(data => {
            if (data.user_id) {
                fetch("/update_progress", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({noquiz:progressPercentage })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        localStorage.setItem("noquiz", progressPercentage);
                    }
                });   
            }
        });*/
        alert("Congratulations! You have completed the quiz.");
        window.location.href = "temp.html"; // Redirect back to roadmap
    } else {
        alert("Try again! You need 100% to pass.");
        window.location.href = "word1.html";
    }
}
// Load question and display image
function loadQuestion() {
    const feedback = document.getElementById('feedback');
    const videoElement = document.getElementById('quiz-video');
    const optionsContainer = document.getElementById('options-container');

    if (currentQuestionIndex >= wordData.length) {
        feedback.textContent = 'Quiz completed!';
        checkQuizCompletion();
        updateProgressBar(true);
        setTimeout(() => {
            window.location.href = 'temp.html';
        }, 2000);
        return;
    }

    const question = wordData[currentQuestionIndex];

    // Ensure the video source is correctly set
    videoElement.src = `/static/vid/${question.word}.mp4`;
    videoElement.load();  // Reload the video
    videoElement.play();  // Auto-play

    // Clear previous options and feedback
    optionsContainer.innerHTML = '';
    feedback.textContent = '';

    // Generate randomized options
    const options = generateOptions(question.word);
    options.forEach((option, index) => {
        const button = document.createElement('button');
        button.classList.add('option');
        button.textContent = option;
        button.onclick = () => checkAnswer(index, question.word, options);
        optionsContainer.appendChild(button);
    });
}


function generateOptions(correctWord) {
    const options = new Set([correctWord]);
    while (options.size < 4) {
        const randomWord = wordData[Math.floor(Math.random() * wordData.length)].word;
        options.add(randomWord);
    }
    return Array.from(options).sort(() => Math.random() - 0.5);
}


// Check answer and provide feedback
function checkAnswer(selectedIndex, correctWord, options) {
    const feedback = document.getElementById('feedback');

    // If answer is correct
    if (options[selectedIndex] === correctWord) {
        correctAnswers++;
        feedback.textContent = 'Correct!';
        updateProgressBar();
    } else {
        feedback.textContent = `Incorrect! Correct answer: ${correctWord}`;
         // Add to incorrect list
    }

    // Proceed to next question
    currentQuestionIndex++;
    setTimeout(loadQuestion, 2000); // Wait 2 seconds before loading next question
}

// Initialize quiz and start
document.addEventListener('DOMContentLoaded', () => {
    initialTotalQuestions = wordData.length; 
    totalQuestions = wordData.length;  
    shuffleArray(wordData); 
    loadQuestion();  
});