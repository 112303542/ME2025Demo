function random_answer(min , max){
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

var answer = random_answer(0 , 100);
var guessCount = 0;

function answer_check(){
    guessCount += 1;
    const valiable = parseInt(document.getElementById('guessNumber').value);

    if(valiable == answer){
        alert('恭喜您猜對了，您一共猜了'+ guessCount +'次。');
        answer = random_answer(0 , 100);
        guessCount = 0;
    }

    else if(valiable < answer){
        let output = document.getElementById('output');
        output.innerHTML = '太小了，請再試一次';
    }
    
    else if(valiable > answer){
        let output = document.getElementById('output');
        output.innerHTML = '太大了，請再試一次';
    }
}