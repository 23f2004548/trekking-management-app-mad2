<script setup>
import { useRouter } from "vue-router"
const router = useRouter()
</script>

<template>
    <div class="landing-page min-vh-100 d-flex flex-column justify-content-between">
        <main class="container mt-5">
            <h1 class="text-center fw-bold" id="title">TrekFlow</h1>
            <div class="text-center mt-3">
                <h3 class="fw-semibold">Conquer Trails. Leave the Chaos Behind.</h3>
            </div>
        </main>
        
        <div class="container" id="community">
            <div class="d-flex justify-content-center gap-4 mb-5" id="button">
                <button class="btn btn-light shadow" @click="router.push('/login')">Login</button>
                <button class="btn btn-light shadow" @click="router.push('/register')">Register</button>
            </div>
        </div>

        <footer class="text-center text-white mb-4">
            <i>Copyright 2026 Trekking Management App. All rights reserved.</i>
        </footer>
    </div>
</template>
