<script setup>
import { ref } from 'vue'

const text = ref("")
</script>

<template>
    <h1>6. 表单绑定 v-model</h1>
    <input v-model="text" placeholder="Type here">
    <p>{{ text }}</p>
</template>