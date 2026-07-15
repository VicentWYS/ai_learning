function add(a, b) {
    return a + b;
}

function multiply(a, b) {
    return a * b;
}

function getMax(a, b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

function getCircleArea(radius) {
    return Math.PI * radius * radius
}

const greet = (name) => {
    return "Hello " + name + ", this is Js";
}

// ============================ 页面按钮绑的调用函数 ============================

function show_add() {
    var result = add(10, 8);
    document.getElementById("demo").innerHTML = result;
}

function show_multiply() {
    var result = multiply(10, 4);
    document.getElementById("demo").innerHTML = result;
}

function show_max() {
    var result = getMax(40, 100);
    document.getElementById("demo").innerHTML = result;
}

function show_circle_area() {
    var result = getCircleArea(1);
    document.getElementById("demo").innerHTML = result.toFixed(2);
}

function show_greet() {
    var result = greet("Tom");
    document.getElementById("demo").innerHTML = result;
}