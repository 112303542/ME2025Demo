document.writeln('<input type="text" id="display" readonly><br><br>');

let buttons=[
    ['0','1','2'],
    ['3','4','5'],
    ['6','7','8'],
    ['9','clear'],
    ['+', '-', '*', '/', '(', ')', '=']
];

for(let row of buttons){
    for(let column of row){
        document.writeln('<button onclick="buttonClick(\'' + column + '\')">' + column + '</button>');
    }
    document.writeln('<br>');
}

function buttonClick(value){
    let display = document.getElementById("display");

    if(value === "clear") display.value =  "";

    else if(value === '='){
        
    }
}