<script setup>
// 声明接受父组件传来的数据
const props = defineProps({
    // 规定 todo 必须是 Object 类型
    // "我这里可以收一个叫 todo 的快递"
    todo: Object
})
</script>

<template>
    <!-- 拿到父组件传来的那条数据里的 text 字段 -->
    <li>{{ todo.text }}</li>
</template>

