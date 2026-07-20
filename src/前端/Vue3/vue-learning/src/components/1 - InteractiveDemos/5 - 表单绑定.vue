<script setup>
import { ref } from 'vue'

const text = ref("")

function onInput(e) {
    text.value = e.target.value
}
</script>

<template>
    <h1>5. 表单绑定</h1>
    <input :value="text" @input="onInput" placeholder="Type here">
    <p>{{ text }}</p>
</template>