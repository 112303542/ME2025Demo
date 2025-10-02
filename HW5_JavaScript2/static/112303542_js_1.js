function random_answer(min , max){
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

var answer = random_answer(0 , 100);
var guessCount = 0;
var time = 0.00;
var stopTimer = null;

function timer(){
    time += 0.01;
    //console.log(time.toFixed(2));
    document.getElementById('output_2').innerHTML = '遊戲時間' + time.toFixed(2) + '秒';
}

function answer_check(){
    console.log(answer);
    let output = document.getElementById('output');
    guessCount += 1;
    const valiable = parseInt(document.getElementById('guessNumber').value);
    let nowtime = new Date();

    if(guessCount == 1) stopTimer = setInterval(timer , 10);

    if(valiable == answer){
        alert('恭喜您猜對了，您一共猜了'+ guessCount +'次，' + '一共花了' + time.toFixed(2) + '秒。');

        const history = document.createElement('li');
        history.textContent = '猜了' + guessCount + '次，耗時' +  time.toFixed(2) + '秒 ' + nowtime.toLocaleString('zh-TW',{timeZone:'Asia/Taipei'});
        document.getElementById('history').appendChild(history);
        
        answer = random_answer(0 , 100);
        guessCount = 0;
        output.innerHTML = '';
        clearInterval(stopTimer);
    }

    else if(valiable < answer){
        output.innerHTML = '太小了，請再試一次';
    }

    else if(valiable > answer){
        output.innerHTML = '太大了，請再試一次';
    }
}