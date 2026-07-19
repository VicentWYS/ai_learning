<script setup>
import {ref} from 'vue'

const today = ref(true)
function toggle(){
    today.value = !today.value
}
</script>

<template>
<h1>7. 条件渲染</h1>
<button @click="toggle">Toggle</button>
<p v-if="today">Today is Saturday.</p>
<p v-else>No, it's Sunday.</p>
</template>