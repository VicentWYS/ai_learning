<script setup>
import { ref, onMounted } from 'vue'

const pElementRef = ref(null)

// 等页面渲染完了，再执行这个大括号里的代码
// 该函数是Vue生命周期的一个钩子hook。
// 可以把它想象成闹钟，闹钟设在“页面渲染完成”那一刻，响了就执行这个函数
// 	Vue 组件从"出生"到"销毁"的各个阶段，onMounted 就是"刚出生、页面刚画好"那个时刻
onMounted(() => {
    // 通过 .value 获取<p> DOM元素，然后通过 .textContent 直接改元素的文字内容
    pElementRef.value.textContent = 'mounted'
})
</script>

<template>
    <h1>10. 生命周期和模板引用</h1>
    <!-- 给这个<p>元素贴个名字标签，让JS代码能找到它 -->
    <p ref="pElementRef">Hello</p>
</template>

<!-- 
页面开始加载
    ↓
<script setup> 里的代码执行
    ↓
const pElementRef = ref(null)  ← 空盒子准备好
    ↓
onMounted(() => {...})  ← 注册了一个"等渲染完再执行"的回调
    ↓
模板渲染：<p ref="pElementRef">Hello</p>  ← 页面出现 "Hello"
    ↓
Vue 自动把 <p> 元素塞进 pElementRef.value
    ↓
渲染完毕，触发 onMounted 回调
    ↓
pElementRef.value.textContent = 'mounted'  ← 文字变成 "mounted"
    ↓
用户看到的是：mounted

-->