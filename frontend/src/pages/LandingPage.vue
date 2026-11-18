<script setup>
import { onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

onMounted(() => {
    document.body.classList.add("landing-page")
})

onUnmounted(() => {
    document.body.classList.remove("landing-page")
})
</script>

<template>
    <div class="landing-page-container min-vh-100 d-flex flex-column justify-content-between py-4">
        <main class="container text-center my-auto">
            <h1 class="fw-bold display-4 text-white" id="title" style="text-shadow: 0 3px 10px rgba(0,0,0,0.6);">
                TrekFlow
            </h1>
            <h4 class="fw-semibold text-white mt-2" style="text-shadow: 0 2px 6px rgba(0,0,0,0.6);">
                Conquer Trails. Leave the Chaos Behind.
            </h4>
            <div class="d-flex justify-content-center gap-3 mt-4">
                <button class="btn btn-light btn-lg px-4 shadow fw-semibold" @click="router.push('/login')">
                    <i class="bi bi-box-arrow-in-right me-1"></i>Login
                </button>
                <button class="btn btn-outline-light btn-lg px-4 shadow fw-semibold" @click="router.push('/register')">
                    <i class="bi bi-person-plus me-1"></i>Register as Trekker
                </button>
            </div>
        </main>

        <footer class="text-center text-white mb-2" style="text-shadow: 0 1px 4px rgba(0,0,0,0.6);">
            <i>Copyright 2026 Trekking Management App. All rights reserved.</i>
        </footer>
    </div>
</template>
