<script setup>
import { computed, ref } from 'vue'

// 输入框正在打的字
const newTodo = ref('')
// 是否隐藏已完成的事项
const hideCompleted = ref(false)

let id = 0

// 待办事项列表
const todos = ref([
    { id: id++, text: 'HTML', done: true },
    { id: id++, text: 'JavaScript', done: true },
    { id: id++, text: 'Vue', done: false }
])

// 添加待办事项
function addTodo() {
    todos.value.push({ id: id++, text: newTodo.value, done: false })
    // 清空输入框
    newTodo.value = ''
}

// 删除某一条事项
function removeTodo(todo) {
    // 保留所有不等于 todo 的项，即等价于：删除等于todo的项
    todos.value = todos.value.filter((t) => t !== todo)
}

// 计算属性，将一个函数变为会自动更新的响应式数据
const filteredTodos = computed(() => {
    // 三元表达式
    return hideCompleted.value
        // 条件为true，只返回未完成的
        ? todos.value.filter((t) => !t.done)
        // 条件为false，返回全部
        : todos.value
})

// ()=>{...} 是ES6的箭头函数，等价于：
// computed(function() {
//     // 计算逻辑
//     return 结果
// })


</script>

<template>
    <h1>9. 计算属性</h1>
    <form @submit.prevent="addTodo">
        <input v-model="newTodo" required placeholder="new todo">
        <button>Add Todo</button>
    </form>
    <ul>
        <li v-for="todo in filteredTodos" :key="todo.id">
            <input type="checkbox" v-model="todo.done">
            <span :class="{ done: todo.done }">
                {{ todo.text }}
            </span>
            <button @click="removeTodo(todo)">X</button>
        </li>
    </ul>
    <!-- 按钮点击时，hideCompleted的值在true/false之间切换 -->
    <button @click="hideCompleted = !hideCompleted">
        {{ hideCompleted ? 'Show all' : 'Hide completed' }}
    </button>
</template>

<style>
.done {
    text-decoration: line-through;
}
</style>


<!-- 
用户点击 "Hide completed" 按钮
        │
        ▼
hideCompleted.value  = false ──变成──▶ true
        │
        ▼
Vue 检测到：hideCompleted 变了！
"computed 内部用到了它，filteredTodos 需要重算！"
        │
        ▼
执行箭头函数：
  hideCompleted.value 现在是 true
  走 ? 分支 → todos.value.filter((t) => !t.done)
  返回 [{ id:2, text:'Vue', done: false }]
        │
        ▼
filteredTodos 的值更新为过滤后的数组
        │
        ▼
模板 v-for="todo in filteredTodos" 发现 filteredTodos 变了
        │
        ▼
页面只渲染 Vue 这一条，HTML 和 JavaScript 隐藏

-->