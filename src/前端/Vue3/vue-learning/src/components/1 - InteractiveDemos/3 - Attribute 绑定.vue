<script setup>
import { ref } from 'vue';

// 声明一个响应式变量
const titleClass = ref("title") 
</script>

<template>
    <h1>3 - Attritube 绑定</h1>
    <!-- 等价于：class=title -->
    <!-- class前面的: 冒号 等价于 "别写死，从 JS 变量里取" -->
    <p :class="titleClass">Make me red</p>
</template>

<style>
.title {
    color: red;
}
</style>