<script setup>
import { ref } from 'vue'

const message = ref('Hello World!')

function reverseMessage() {
    // 1.将字符串按空字符串分割，即将每个字符拆开，返回一个字符数组
    // 2.反转数组元素的顺序
    // 3.将数组元素用空字符串连接起来，重新组合成一个字符串
    message.value = message.value.split('').reverse().join('')
}

function notify() {
    alert('navigation was prevented.')
}
</script>

<template>
    <h1>2. 处理用户输入</h1>

    <p>{{ message }}</p>

    <button @click="reverseMessage">Reverse Message</button>

    <button @click="message += '!'">Append "!"</button>

    <a href="https://vuejs.org" @click.prevent="notify">A link with e.preventDefault()</a>
</template>

<style>
button,
a {
    display: block;
    margin-bottom: 1em;
}
</style>