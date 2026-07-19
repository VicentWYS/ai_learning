<script setup>
import { ref } from 'vue'

let id = 0

const todos = ref([
    { id: id++, text: "Learn HTML" },
    { id: id++, text: "Learn JavaScript" },
    { id: id++, text: "Learn Vue" }
])

const newTodo = ref('')

function addTodo() {
    todos.value.push({ id: id++, text: newTodo.value })
    // 清空输入框
    newTodo.value = ''
}

function removeTodo(todo) {
    todos.value = todos.value.filter((item) => item !== todo)
}
</script>

<template>
    <h1>8. 列表渲染</h1>
    <!-- 事件修饰符：组织表单的默认提交行为（刷新页面），
     改为调用 addTodo -->
    <form @submit.prevent="addTodo">
        <!-- 双向绑定：输入框内容变化时，newTodo 自动更新，
         newTodo 变化时输入框也自动更新 -->
        <input v-model="newTodo" required placeholder="new todo">
        <button>Add Todo</button>
    </form>
    <ul>
        <li v-for="todo in todos" :key="todo.id">
            {{ todo.text }}
            <button @click="removeTodo(todo)">X</button>
        </li>
    </ul>

</template>