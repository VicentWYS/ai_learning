<script setup>
import { ref } from 'vue'
import ChileDemo from './15 - 插槽-Child.vue'

const msg = ref('from parent')
</script>

<template>
    <h1>15. 插槽</h1>
    <ChileDemo>Message: {{ msg }}</ChileDemo>
    
    <!-- 以下情况才会出现子组件中的默认值 -->
    <!-- <ChileDemo></ChileDemo> -->
</template>

<!-- 
父组件准备了一条消息 msg = "from parent"
        |
        v
把 "Message: from parent" 塞进 <ChileDemo>...</ChileDemo> 标签中间
        |
        v
Vue 找到子组件里的 <slot> 坑位
        |
        v
把父组件塞进来的内容填进去，替换掉默认的 "Fallback content"
        |
        v
页面上最终显示：  Message: from parent

-->