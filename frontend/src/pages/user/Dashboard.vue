<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const user = ref(null)

onMounted(async () => {
    const token = localStorage.getItem("token")
    if (token) {
        try {
            const res = await axios.get("http://localhost:5000/whoami", {
                headers: { Authorization: `Bearer ${token}` }
            })
            user.value = res.data
        } catch (e) {
            console.error(e)
        }
    }
})
</script>

<template>
    <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold mb-1">Trekker Dashboard</h2>
                <p class="text-muted small">Welcome, {{ user?.name || 'Trekker' }}</p>
            </div>
            <span class="badge bg-success fs-6">Role: Trekker</span>
        </div>

        <div class="alert alert-success py-3">
            <h5 class="alert-heading fw-bold mb-1">Authentication & Access Verified</h5>
            <p class="mb-0 small">You are logged in as a registered Trekker. Trek browsing, booking and history will be connected in Milestone 5.</p>
        </div>
    </div>
</template>
