<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
    data: Array,
    columns: Array,
    filterKey: String
})

const sortKey = ref('')
const sortOrders = ref(props.columns.reduce((o, key) => (o[key] = 1), o), {})
</script>