// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    const translateButton = document.getElementById('translateButton');
    const englishInput = document.getElementById('englishInput');
    const islOutput = document.getElementById('islOutput');
    const videoSection = document.getElementById('videoSection');
    const signVideo = document.getElementById('signVideo');
    const videoPlaceholder = document.getElementById('videoPlaceholder');
    const currentWordElement = document.getElementById('currentWord');
    const videoUnavailable = document.getElementById('videoUnavailable');
    const exampleElements = document.querySelectorAll('.example');
    
    if (!translateButton || !englishInput || !islOutput) return;
    
    // Handle translation
    translateButton.addEventListener('click', function() {
        translateSentence();
    });
    
    // Handle Enter key in textarea
    englishInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            translateSentence();
        }
    });
    
    // Handle example sentences
    exampleElements.forEach(example => {
        example.addEventListener('click', function() {
            const sentence = this.dataset.sentence;
            englishInput.value = sentence;
            translateSentence();
        });
    });
    
    // Translation function
    function translateSentence() {
        const sentence = englishInput.value.trim();
        
        if (!sentence) {
            showMessage('Please enter a sentence to translate', 'error');
            return;
        }
        
        // Show loading state
        islOutput.innerHTML = '<div class="loading-spinner"></div>';
        
        // Send translation request
        fetch('/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ sentence: sentence }),
        })
        .then(response => response.json())
        .then(data => {
            displayTranslation(data);
        })
        .catch(error => {
            console.error('Error:', error);
            islOutput.innerHTML = '<p class="error-message">Error translating sentence. Please try again.</p>';
            showMessage('Error translating sentence', 'error');
        });
    }
    
    // Display translation result
    function displayTranslation(data) {
        // Clear previous results
        islOutput.innerHTML = '';
        
        if (!data.isl_sentence) {
            islOutput.innerHTML = '<p class="error-message">Could not translate sentence. Please try again with a different sentence.</p>';
            return;
        }
        
        // Create word elements
        const wordsWithVideos = data.words_with_videos || [];
        
        wordsWithVideos.forEach(wordInfo => {
            const wordElement = document.createElement('span');
            wordElement.textContent = wordInfo.word;
            wordElement.className = 'isl-word';
            
            if (wordInfo.hasVideo) {
                wordElement.classList.add('has-video');
                wordElement.title = 'Click to see video';
                
                // Add click event to show video
                wordElement.addEventListener('click', function() {
                    playSignVideo(wordInfo.word);
                });
            }
            
            islOutput.appendChild(wordElement);
            islOutput.appendChild(document.createTextNode(' '));
        });
        
        // Show or scroll to video section
        videoSection.style.display = 'block';
        videoPlaceholder.style.display = 'flex';
        signVideo.style.display = 'none';
        videoUnavailable.style.display = 'none';
        currentWordElement.textContent = '';
        
        // Initialize session logging
        startLearningSession(data.isl_sentence.split(' '));
    }
    
    // Play sign language video for a word
    function playSignVideo(word) {
        // Show loading state
        videoPlaceholder.style.display = 'flex';
        videoPlaceholder.innerHTML = '<div class="loading-spinner"></div>';
        signVideo.style.display = 'none';
        videoUnavailable.style.display = 'none';
        currentWordElement.textContent = word;
        
        // Fetch video URL
        fetch(`/play_video/${encodeURIComponent(word)}`)
            .then(response => response.json())
            .then(data => {
                if (data.path) {
                    signVideo.src = data.path;
                    signVideo.load();
                    signVideo.onloadeddata = function() {
                        videoPlaceholder.style.display = 'none';
                        signVideo.style.display = 'block';
                        videoUnavailable.style.display = 'none';
                        signVideo.play();
                    };
                    signVideo.onerror = function() {
                        showVideoUnavailable(word);
                    };
                } else {
                    showVideoUnavailable(word);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showVideoUnavailable(word);
            });
    }
    
    function showVideoUnavailable(word) {
        videoPlaceholder.style.display = 'flex';
        videoPlaceholder.innerHTML = '<p>Video not available</p>';
        signVideo.style.display = 'none';
        videoUnavailable.style.display = 'block';
    }
    
    // Learning session tracking
    let sessionStart = null;
    let practiceWords = [];
    
    function startLearningSession(words) {
        if (!sessionStart) {
            sessionStart = new Date();
            practiceWords = words;
            
            // Log session after 30 seconds of activity
            setTimeout(logLearningSession, 30000);
        } else {
            // Update words being practiced
            practiceWords = [...new Set([...practiceWords, ...words])];
        }
    }
    
    function logLearningSession() {
        if (!sessionStart || practiceWords.length === 0) return;
        
        const sessionDuration = Math.round((new Date() - sessionStart) / 1000);
        
        // Only log if user spent at least 10 seconds
        if (sessionDuration < 10) return;
        
        // Log session data (simplified for this demo)
        console.log('Learning session logged:', {
            duration: sessionDuration,
            words: practiceWords
        });
        
        // Reset session data
        sessionStart = null;
        practiceWords = [];
    }
    
    // Log session on page unload
    window.addEventListener('beforeunload', logLearningSession);
}

function showMessage(message, type = 'info') {
    const messageContainer = document.getElementById('messageContainer');
    
    if (!messageContainer) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    messageElement.textContent = message;
    
    messageContainer.appendChild(messageElement);
    
    // Remove message after 5 seconds
    setTimeout(() => {
        messageElement.classList.add('fade-out');
        setTimeout(() => {
            messageContainer.removeChild(messageElement);
        }, 500);
    }, 5000);
}