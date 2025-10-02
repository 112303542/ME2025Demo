function random_answer(min,max){
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

var answer = random_answer(0,100);
var guessCount = 0;

