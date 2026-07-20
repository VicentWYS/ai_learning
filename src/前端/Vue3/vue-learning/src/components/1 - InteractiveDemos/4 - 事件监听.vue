<script setup>
import { ref } from 'vue'

// 返回一个包装盒对象
const count = ref(0)
function increment() {
    // 更新组件状态，在script中，必须手动拆盒，即count.value
    count.value++
}
</script>

<template>
    <h1>4. 事件监听</h1>
    <!-- 在模板中自动拆盒 -->
    <button @click="increment">Count is: {{ count }}</button>
</template>