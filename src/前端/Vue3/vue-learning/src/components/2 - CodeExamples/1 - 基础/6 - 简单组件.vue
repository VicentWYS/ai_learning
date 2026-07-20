<!-- Vue父传子组件的示例 -->

<script setup>
import { ref } from 'vue'
import TodoItem from './组件/TodoItem.vue';

const groceryList = ref([
    { id: 0, text: 'Vegetables' },
    { id: 1, text: 'Cheese' },
    { id: 2, text: 'Whatever else humans are supposed to eat' }
])
</script>

<template>
    <h1>6. 简单组件</h1>
    <ol>
        <!-- <TodoItem></TodoItem> 使用子组件 -->
        <!-- v-for... 循环渲染 -->
        <!-- :todo="item" 把 item 打包进名叫 todo 的快递盒，递给子组件 -->
        <!-- :key="item.id 唯一标识 -->
        <TodoItem v-for="item in groceryList" :todo="item" :key="item.id"></TodoItem>
        <!-- key = 给列表中每个元素贴一个唯一的身份证号，让 Vue 增删改查时能精确找到目标，既高效又准确。 -->
    </ol>
</template>

<!--     
        父组件                        子组件
┌─────────────────────┐         ┌─────────────────┐
│ groceryList = [     │         │ props = {       │
│   {id:0, text:'..'} │──:todo──│   todo: {       │
│   {id:1, text:'..'} │  传递   │     id: 0,      │
│   {id:2, text:'..'} │         │     text: '...' │
│ ]                   │         │   }             │
└─────────────────────┘         └─────────┬───────┘
                                          │
                                    {{ todo.text }}
                                     渲染到页面上
-->

<!-- 
groceryList（数据）
→ v-for 拆成 item（每一条）
→ 通过 :todo（快递通道）
→ 传给子组件 
→ 子组件用 props.todo（接收）
→ todo.text（取出文字）
→ 显示在 <li> 里。
-->