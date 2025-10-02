function random_answer(min , max){
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

var answer = random_answer(0 , 100);
var guessCount = 0;
var time = 0;

function timer(){
    time ++ ;
}

function answer_check(){

    let output = document.getElementById('output');
    guessCount += 1;
    const valiable = parseInt(document.getElementById('guessNumber').value);

    let stop = setInterval(timer,1000);

    if(valiable == answer){
        alert('恭喜您猜對了，您一共猜了'+ guessCount +'次，' + '一共花了' + stop + '秒。');
        answer = random_answer(0 , 100);
        guessCount = 0;
        output.innerHTML = '';
        clearInterval(timer);
    }

    else if(valiable < answer){
        output.innerHTML = '太小了，請再試一次';
    }

    else if(valiable > answer){
        output.innerHTML = '太大了，請再試一次';
    }
}