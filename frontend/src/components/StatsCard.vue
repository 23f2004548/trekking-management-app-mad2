<script setup>
const props = defineProps({
    card_title: String,
    card_value: [String, Number]
})
</script>

<template>
    <div class="stats-card">
        <h6>{{ props.card_title }}</h6>
        <p>{{ props.card_value }}</p>
    </div>
</template>

<style scoped>
.stats-card {
    padding: 16px;
    background: #fff;
    border-radius: 10px;
    border: 1px solid #e9ecef;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.stats-card h6 {
    color: #6c757d;
    font-size: 13px;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 6px;
}
.stats-card p {
    font-size: 28px;
    font-weight: bold;
    color: #212529;
    margin: 0;
}
</style>
