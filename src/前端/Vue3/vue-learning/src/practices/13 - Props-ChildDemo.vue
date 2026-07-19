<script setup>
const props = defineProps({
    msg: String
})
</script>

<template>
    <!-- 
     1. 如果 msg 有值，就显示 msg；
     2. 如果 msg 是空的（没传过来），就显示 "No props passed yet" 这段兜底文字。 -->
    <p>{{ msg || 'No props passed yet' }}</p>
</template>