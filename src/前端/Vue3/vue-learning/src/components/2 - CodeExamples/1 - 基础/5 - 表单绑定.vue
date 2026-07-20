<!-- 可以使用 v-model 指令在状态和表单输入之间创建双向绑定 -->

<script setup>
import { ref } from 'vue'

const text = ref('Edit me')
const checked = ref(true)
const checkedNames = ref(['Jack'])
const picked = ref('One')
const selected = ref('A')
const multiSelected = ref(['A'])
</script>

<template>
    <h1>5. 表单绑定</h1>

    <div>
        <h2>Text Input</h2>
        <input v-model="text">
        <p>{{ text }}</p>
    </div>


    <div>
        <h2>Checkbox</h2>
        <input type="checkbox" id="checkbox" v-model="checked">
        <!-- <label for="xxx"> 会和 id="xxx" 的表单控件绑定在一起。当用户点击 label 文本时，浏览器会自动把焦点移到对应的控件上。 -->
        <!-- 即：点击 "Checked: true" 这段文字也能勾选/取消 -->
        <label for="checkbox">Checked: {{ checked }}</label>
    </div>

    <div>
        <h2>Multi checkbox</h2>
        <div>
            <!-- 根据勾选状态将 value 加入或移出数组，这是 Vue 设计好的机制 -->
            <input type="checkbox" id="jack" value="Jack" v-model="checkedNames">
            <label for="jack">Jack</label>
        </div>

        <div>
            <input type="checkbox" id="john" value="John" v-model="checkedNames">
            <label for="john">John</label>
        </div>

        <div>
            <input type="checkbox" id="mike" value="Mike" v-model="checkedNames">
            <label for="mike">Mike</label>
        </div>

        <!-- 数组中，是全部被选中元素的value -->
        <p>Checked names: {{ checkedNames }}</p>
    </div>

    <div>
        <h2>Radio</h2>
        <input type="radio" id="one" value="One" v-model="picked">
        <label for="one">One</label>
        <br>
        <input type="radio" id="two" value="Two" v-model="picked">
        <label for="two">Two</label>
        <p>Picked: {{ picked }}</p>
    </div>

    <div>
        <h2>Select</h2>
        <select v-model="selected">
            <option disabled value="">Please select one</option>
            <option>A</option>
            <option>B</option>
            <option>C</option>
        </select>
        <p>Seleced: {{ selected }}</p>
    </div>

    <div>
        <h2>Multi Select</h2>
        <select v-model="multiSelected" multiple style="width: 100px">
            <option>A</option>
            <option>B</option>
            <option>C</option>
        </select>
        <p>Selected: {{ multiSelected }}</p>
    </div>
</template>