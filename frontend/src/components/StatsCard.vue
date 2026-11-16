<script setup>
const props = defineProps({
    card_title: String,
    card_value: [String, Number],
    icon: {
        type: String,
        default: "bi-graph-up"
    }
})
</script>

<template>
    <div class="stat-card p-3 shadow-sm h-100">
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <div class="text-muted small fw-semibold text-uppercase">{{ props.card_title }}</div>
                <div class="stat-number mt-1">{{ props.card_value }}</div>
            </div>
            <div class="stat-icon">
                <i :class="'bi ' + props.icon"></i>
            </div>
        </div>
    </div>
</template>
