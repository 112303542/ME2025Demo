function random_answer(min,max){
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

var answer = random_answer(0,100);
var guessCount = 0;

function answer_check(valiable){
    guessCount += 1;
    const valiable = document.getElementById('guessNumber');
    if(valiable == answer){
        alert('恭喜您猜對了，您一共猜了'+ guessCount +'次。');
    }
    else if(valiable < answer){
        alert('太小了，請再試一次');
    }
    else if(valiable > answer){
        alert('太大了，請再試一次');
    }
}
