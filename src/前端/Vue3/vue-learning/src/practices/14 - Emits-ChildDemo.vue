<script setup>

// 子组件声明：我能发出一种叫response的信号频道
const emit = defineEmits(['response'])

// 组件一加载就直接发出信号，内容为 'hello from child'
emit('response', 'hello from child')
</script>

<template>
    <p>Child component</p>
</template>