<script setup>
import { ref, watchEffect } from 'vue'

// Github 开放API，用于获取Vue核心仓库的commit记录（每次取3条）
const API_URL = `https://api.github.com/repos/vuejs/core/commits?per_page=3&sha=`

const branches = ['main', 'minor']

// 当前选中的分支，默认为 'main'
const currentBranch = ref(branches[0])

// 存储获取到的提交记录
const commits = ref([])

// 该effect会立即运行，并且在 currentBranch.value 改变时重新运行
watchEffect(
    async () => {
        // 当用户切换分支时（比如改成 'minor'）：
        // → currentBranch.value 变化 
        // → watchEffect 自动重新触发 
        // → 重新 fetch 该分支的 commits
        const url = `${API_URL}${currentBranch.value}`
        commits.value = await (await fetch(url)).json()
    }
)

// 字符串截断工具函数，作用是只保留文本的第一行
function truncate(v) {
    // 找到第一个换行符的位置
    const newline = v.indexOf('\n')
    // 有换行就截断，没有就原因返回（说明本身就只有一行）
    return newline > 0 ? v.slice(0, newline) : v
}

// 日期格式化工具函数，用来把 GitHub API 返回的 ISO 8601 日期字符串变得更好读
function formatDate(v) {
    // 用空格替换匹配到的字符
    return v.replace(/T|Z/g, ' ')
}
</script>

<template>
    <h1>Latest Vue Code Commits</h1>
    <template v-for="branch in branches">
        <input type="radio" :id="branch" :value="branch" name="branch" v-model="currentBranch">
        <label :for="branch">{{ branch }}</label>
    </template>
</template>