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
                <h2 class="fw-bold mb-1">Admin Dashboard</h2>
                <p class="text-muted small">Welcome, {{ user?.name || 'Administrator' }}</p>
            </div>
            <span class="badge bg-primary fs-6">Role: Admin</span>
        </div>

        <div class="alert alert-info py-3">
            <h5 class="alert-heading fw-bold mb-1">Role-Based Access Verified</h5>
            <p class="mb-0 small">You are logged in with administrative privileges. Full dashboard management will be connected in Milestone 3.</p>
        </div>
    </div>
</template>
