function random_answer(min,max){
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
let answer = random_answer(0,100);
