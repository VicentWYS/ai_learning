<script setup>
import { ref } from 'vue'
import ChildDemo from './14 - Emits-ChildDemo.vue'

const childMsg = ref('No child msg yet')
</script>

<template>
    <h1>14. Emits</h1>
    <!-- 把子组件放进来 -->
    <!-- 竖着耳朵听着，一旦子组件喊了 response 频道, 就把喊的内容塞到 childMsg 里 -->
    <ChildDemo @response="(msg) => childMsg = msg" />
    <p>{{ childMsg }}</p>
</template>