<script setup>
import { reactive } from 'vue';
import { ref } from 'vue'

// reactive 实现
const counter = reactive({
  count: 0
})

// ref 实现
const message = ref('Hello world!')


</script>

<template>
  <h1>2. 响应式：reactive & ref</h1>
  <p>reactive实现：{{ counter.count }}</p>
  <p>ref实现：{{ message }}</p>
</template>