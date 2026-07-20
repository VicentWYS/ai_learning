<script setup>
import { ref } from 'vue'

const message = ref('Hello World!')
</script>

<template>
    <h1>1. Hello World!</h1>
    <p>{{ message }}</p>
</template>