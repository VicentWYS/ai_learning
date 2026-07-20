<script setup>
import { ref } from 'vue'

const message = ref('Hello World!')
const isRed = ref(true)
const color = ref('green')

function toggleRed() {
    isRed.value = !isRed.value
}

function toggleColor() {
    color.value = color.value === 'green' ? 'blue' : 'green'
}
</script>

<template>
    <h1>3. Attribute 绑定</h1>
    <p>
        <!-- :title 语法是 v-bind:title 的简写 -->
        <!-- 将 <span> 元素的 HTML title 属性动态绑定到 Vue 响应式变量 message 上 -->
        <!-- title 是 HTML 原生属性——当用户鼠标悬停在元素上时，浏览器会显示 title 的内容作为提示文本 -->
        <!-- 渲染到 DOM 后变成：<span title="Hello World!">...</span> -->
        <span :title="message">
            Hover your mouse over me for a few seconds to see my dynamically bound title!
        </span>
    </p>

    <!-- 当 isRed 为 true 时，red 这个类会被添加到元素上；为 false 时则移除 -->
    <!-- 渲染到 DOM 后变成：<p :class="{ red: isRed }" @click="toggleRed">...</p> -->
    <p :class="{ red: isRed }" @click="toggleRed">
        This should be red... but click me to toggle it.
    </p>

    <!-- 渲染到 DOM 后变成：<p style="color: green;">...</p> -->
    <p :style="{ color }" @click="toggleColor">
        This should be green, and should toggle between green and blue on click.
    </p>
</template>

<style>
.red {
    color: red;
}
</style>