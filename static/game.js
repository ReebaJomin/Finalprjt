const images = [
    '../assets/hello.jpg', '../assets/hello1.jpg',
    '../assets/goodbye.jpg', '../assets/goodbye1.jpg',
    '../assets/please.jpg', '../assets/please1.jpg',
    '../assets/yes.jpg', '../assets/yes1.jpg',
    '../assets/no.jpg', '../assets/no1.jpg',
    '../assets/Thanks.jpg', '../assets/Thanks1.jpg',
  ];
  
  let attempts = 0;
  let firstCard = null;
  let secondCard = null;
  
  function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
  }
  
  function createBoard() {
    const gameBoard = document.getElementById('game-board');
    shuffle(images);
    
    images.forEach(image => {
      const card = document.createElement('div');
      card.classList.add('card');
      card.dataset.image = image;
      
      const img = document.createElement('img');
      img.src = image;
      card.appendChild(img);
      
      card.addEventListener('click', flipCard);
      
      gameBoard.appendChild(card);
    });
  }
  
  function flipCard() {
    if (this === firstCard) return;
    
    this.classList.add('flipped');
    
    if (!firstCard) {
      firstCard = this;
      return;
    }
    
    secondCard = this;
    attempts++;
    document.getElementById('attempts').textContent = attempts;
  
    const firstImageBase = firstCard.dataset.image.replace(/\d+\.jpg$/, '.jpg');
    const secondImageBase = secondCard.dataset.image.replace(/\d+\.jpg$/, '.jpg');
    
    if (firstImageBase === secondImageBase) {
      // Match found
      firstCard.removeEventListener('click', flipCard);
      secondCard.removeEventListener('click', flipCard);
      resetBoard();
    } else {
      // No match
      setTimeout(() => {
        firstCard.classList.remove('flipped');
        secondCard.classList.remove('flipped');
        resetBoard();
      }, 1000);
    }
  }
  
  function resetBoard() {
    [firstCard, secondCard] = [null, null];
  }
  
  createBoard();
  