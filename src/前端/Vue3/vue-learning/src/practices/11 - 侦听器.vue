<script setup>
// 侦听器：盯着某个值，值一变就执行你指定的函数
import { ref, watch } from 'vue'

const todoId = ref(1)
const todoData = ref(null)

// 请求数据，使其更新页面
async function fetchData() {
    // 清空旧数据
    todoData.value = null
    // 发请求
    const res = await fetch(`https://jsonplaceholder.typicode.com/todos/${todoId.value}`)
    // 把返回的JSON存起来
    todoData.value = await res.json()
}

// 页面刚加载时，先主动请求一次数据，否则页面是空白的
fetchData()

// 盯着 todoId，只要它一变，就自动调用 fetchData
watch(todoId, fetchData)
</script>

<template>
    <h1>11. 侦听器</h1>

    <p>Todo id: {{ todoId }}</p>

    <!-- 点击让todoId+1 -->
    <!-- 数据还没回来时禁用按钮，防止狂点 -->
    <button @click="todoId++" :disabled="!todoData">Fetch next todo</button>

    <!-- 没数据时显示加载中 -->
    <p v-if="!todoData">Loading...</p>
    <!-- 有数据就格式化显示 -->
    <!-- <pre>会保留内容原格式 -->
    <pre v-else>{{ todoData }}</pre>
</template>

<!-- 
页面加载
    ↓
todoId = 1, todoData = null
    ↓
fetchData() 立刻执行 → 请求第 1 条数据 → todoData 有值了 → 页面显示数据
    ↓
同时，watch(todoId, fetchData) 开始"盯梢"
    ↓
用户点击按钮 → todoId 变成 2
    ↓
watch 发现了 → 自动调 fetchData()
    ↓
todoData 先变成 null → 页面显示 "Loading..."，按钮变灰
    ↓
请求第 2 条数据 → todoData 有值了 → 页面更新
    ↓
再点按钮 → todoId 变成 3 → 同上循环...

-->