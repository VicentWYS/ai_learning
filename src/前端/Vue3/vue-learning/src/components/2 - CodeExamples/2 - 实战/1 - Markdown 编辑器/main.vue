<!-- 一个简单的 Markdown 编辑器 -->

<script setup>
import { marked } from 'marked'
import { debounce } from 'lodash-es'
import { ref, computed } from 'vue'
// marked：将 Markdown 文本解析为 HTML
// debounce：防抖函数，避免高频输入时频繁触发渲染


const input = ref('# hello')

// 是一个计算属性，每当 input.value 变化时，自动调用 marked() 将 Markdown 转为 HTML
const output = computed(() => marked(input.value))

// 是一个经过 100ms 防抖的事件处理函数。用户输入停止 100ms 后才更新 input，减少不必要的解析开销
const update = debounce((e) => {
    input.value = e.target.value
}, 100)

</script>

<template>
    <div class="editor">
        <!-- 左侧编辑区 -->
        <!-- 绑定 input 的值，输入时触发 update -->
        <textarea class="input" :value="input" @input="update"></textarea>

        <!-- 右侧预览区 -->
        <!-- 通过 v-html 将 output（Markdown 转成的 HTML）直接渲染出来 -->
        <div class="output" v-html="output"></div>
    </div>
</template>

<style>
body {
    margin: 0;
}

.editor {
    height: 100vh;
    display: flex;
}

.input,
.output {
    overflow: auto;
    /* 左右各占50%宽度 */
    width: 50%;
    height: 100%;
    box-sizing: border-box;
    padding: 0 20px;
}

.input {
    border: none;
    border-right: 1px solid #ccc;
    resize: none;
    outline: none;
    background-color: #f6f6f6;
    font-size: 14px;
    /* 等宽字体 */
    font-family: 'Monaco', courier, monospace;
    padding: 20px;
}

code {
    color: #f66;
}
</style>