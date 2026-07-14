// 弹出警告框
function window_alert() {
    window.alert(5 + 6);
}

// 操作html元素
function inner_html() {
    document.getElementById("demo").innerHTML = "内容已修改"
}

// 直接写到html文档中
// 在文档已完成加载后执行 document.write，整个 HTML 页面将被覆盖。
function document_write() {
    document.write(Date())
}

// 写到控制台
function console_log(){
    console.log(12)
}