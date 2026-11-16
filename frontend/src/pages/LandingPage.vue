<script setup>
import { useRouter } from "vue-router"
const router = useRouter()
</script>

<template>
    <div class="landing">
        <h1 class="display-4 fw-bold">Trekking Management Application V2</h1>
        <p class="lead text-muted">Explore treks, manage expeditions, and track bookings seamlessly</p>
        <div class="d-flex gap-3 justify-content-center mt-4">
            <button class="btn btn-primary btn-lg px-4" @click="router.push('/login')">Login</button>
            <button class="btn btn-outline-primary btn-lg px-4" @click="router.push('/register')">Register as Trekker</button>
        </div>
    </div>
</template>

<style scoped>
.landing {
    min-height: 85vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 20px;
}
</style>
