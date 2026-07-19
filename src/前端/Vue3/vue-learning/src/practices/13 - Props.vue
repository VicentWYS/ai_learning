<script setup>
import { ref } from 'vue'
import ChildDemo from './13 - Props-ChildDemo.vue'


const greeting = ref('Hello from parent')
</script>

<template>
    <h1>13. Props</h1>
    <ChildDemo :msg="greeting"></ChildDemo>
</template>