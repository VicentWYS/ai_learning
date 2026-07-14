// ========== 1. 普通函数声明 ==========

// 两数相加，返回它们的和
function add(a, b) {
    return a + b;
}

// 两数相乘，返回它们的积
function multiply(a, b) {
    return a * b;
}

// 返回两个数中较大的那个
function getMax(a, b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

// 计算圆的面积（π × 半径的平方）
function getCircleArea(radius) {
    return Math.PI * radius * radius;
}

// ========== 2. 箭头函数（ES6） ==========

// 箭头函数：返回一句问候语
const greet = (name) => {
    return "你好，" + name + "！欢迎学习 JavaScript！";
};

// ========== 3. 页面按钮绑定的调用函数 ==========

function show_add() {
    var result = add(10, 7);
    document.getElementById("demo").innerHTML = "add(10, 7) 的返回值 = " + result;
}

function show_multiply() {
    var result = multiply(6, 8);
    document.getElementById("demo").innerHTML = "multiply(6, 8) 的返回值 = " + result;
}

function show_max() {
    var result = getMax(25, 18);
    document.getElementById("demo").innerHTML = "getMax(25, 18) 的返回值 = " + result;
}

function show_circle_area() {
    var result = getCircleArea(5);
    document.getElementById("demo").innerHTML = "getCircleArea(5) 的返回值 ≈ " + result.toFixed(2);
}

function show_greet() {
    var result = greet("小明");
    document.getElementById("demo").innerHTML = "greet('小明') 的返回值 = " + result;
}
