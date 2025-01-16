let currentQuestionIndex = 0;
let correctAnswers = 0;
let incorrectQuestions = [];
let answeredQuestions = [];
let totalQuestions = 0;

// Word data (hardcoded for now)
let wordData = [
    { word: 'A', url: 'https://www.youtube.com/watch?v=8xWxsYN69SQ' },
    { word: 'B', url: 'https://www.youtube.com/watch?v=YU5PLKBV2Us' },
    { word: 'C', url: 'https://www.youtube.com/watch?v=XzhAhPklmPY' },
    { word: 'D', url: 'https://www.youtube.com/watch?v=YUC0eWGkB8s' },
    { word: 'E', url: 'https://www.youtube.com/watch?v=QNXEgEqapoU' },
    { word: 'F', url: 'https://www.youtube.com/watch?v=0b6uPi6wWCk' },
    { word: 'G', url: 'https://www.youtube.com/watch?v=L4inmmLNfxU' },
    { word: 'H', url: 'https://www.youtube.com/watch?v=qYXNC802fBY' },
    { word: 'J', url: 'https://www.youtube.com/watch?v=8VbcMW1if2k' },
    { word: 'K', url: 'https://www.youtube.com/watch?v=py3K_M7iQPc' },
    { word: 'L', url: 'https://www.youtube.com/watch?v=MMjzmbKkIzA' },
    { word: 'M', url: 'https://www.youtube.com/watch?v=2Ue2zgU1cWw' },
    { word: 'N', url: 'https://www.youtube.com/watch?v=YoFq5pajSOg' },
    { word: 'O', url: 'https://www.youtube.com/watch?v=dH8pdcctqXw' },
    { word: 'P', url: 'https://www.youtube.com/watch?v=nIPTdkuMf60' },
    { word: 'Q', url: 'https://www.youtube.com/watch?v=VLXCN51tv1A' },
    { word: 'R', url: 'https://www.youtube.com/watch?v=7QjGd2SErW8' },
    { word: 'S', url: 'https://www.youtube.com/watch?v=wySbmZlcwxk' },
    { word: 'T', url: 'https://www.youtube.com/watch?v=L80UVAXb1MU' },
    { word: 'U', url: 'https://www.youtube.com/watch?v=JGnDANT5dJ8' },
    { word: 'V', url: 'https://www.youtube.com/watch?v=eJ7j6vx-L9c' },
    { word: 'W', url: 'https://www.youtube.com/watch?v=fZr8y4dU0C0' },
    { word: 'X', url: 'https://www.youtube.com/watch?v=r5ywVC44MeY' },
    { word: 'Y', url: 'https://www.youtube.com/watch?v=ayrubiIOQnc' },
    { word: 'Z', url: 'https://www.youtube.com/watch?v=r8zkVbgQduo' },
    { word: 'i', url: 'https://www.youtube.com/watch?v=P-k3HOBisv8' }
];

// Shuffle function for randomizing questions
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

// Update progress bar after each correct answer
function updateProgressBar() {
    const progressBar = document.getElementById('quiz-progress');
    const progressText = document.getElementById('progress-text');

    const progressPercentage = (correctAnswers / totalQuestions) * 100;
    progressBar.value = progressPercentage;
    progressText.textContent = `${Math.round(progressPercentage)}% completed`;
}

// Extract YouTube ID from URL
function getYouTubeIDFromURL(url) {
    const regex = /(?:youtube\.com\/(?:[^\/\n\s]+\/[^\n\s]+\/|\S+\?v=|(?:v|e(?:mbed))\/)([a-zA-Z0-9_-]{11}))/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

// Load question and display video
function loadQuestion() {
    // If we've completed all questions correctly
    if (currentQuestionIndex >= wordData.length && incorrectQuestions.length === 0) {
        document.getElementById('feedback').textContent = 'Quiz completed!';
        return;
    }

    // If there are incorrect answers, continue with them
    if (currentQuestionIndex >= wordData.length) {
        wordData = [...incorrectQuestions];
        incorrectQuestions = [];
        currentQuestionIndex = 0;
        shuffleArray(wordData);
    }

    const question = wordData[currentQuestionIndex];
    const iframeElement = document.getElementById('quiz-video');
    const optionsContainer = document.getElementById('options-container');
    const feedback = document.getElementById('feedback');

    // Set video to autoplay
    iframeElement.src = `https://www.youtube.com/embed/${getYouTubeIDFromURL(question.url)}?autoplay=1`;

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

// Generate random options for the question
function generateOptions(correctWord) {
    const options = new Set([correctWord]);
    while (options.size < 4) {
        const randomWord = wordData[Math.floor(Math.random() * wordData.length)].word;
        options.add(randomWord);
    }
    return Array.from(options).sort(() => Math.random() - 0.5); // Shuffle options
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
        incorrectQuestions.push(wordData[currentQuestionIndex]); // Add to incorrect list
    }

    // Proceed to next question
    currentQuestionIndex++;
    setTimeout(loadQuestion, 2000); // Wait 2 seconds before loading next question
}

// Initialize quiz and start
document.addEventListener('DOMContentLoaded', () => {
    totalQuestions = wordData.length;  // Set total questions count
    shuffleArray(wordData);  // Shuffle the questions
    loadQuestion();  // Load the first question
});
