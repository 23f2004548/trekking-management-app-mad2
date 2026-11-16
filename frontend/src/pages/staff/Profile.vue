<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const profile = ref({
    name: "",
    email: "",
    phone_number: "",
    specialization: "",
    status: ""
})
const loading = ref(true)
const error = ref("")
const success = ref("")

async function fetchProfile() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/staff/profile`, {
            headers: { Authorization: "Bearer " + token }
        })
        profile.value = res.data
    } catch (err) {
        error.value = "Failed to load profile"
    } finally {
        loading.value = false
    }
}

async function saveProfile() {
    error.value = ""
    success.value = ""
    try {
        await axios.put(`${BASE_URL}/staff/profile`, {
            name: profile.value.name,
            phone_number: profile.value.phone_number,
            specialization: profile.value.specialization
        }, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = "Profile updated successfully"
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to update profile"
    }
}

onMounted(() => {
    fetchProfile()
})
</script>

<template>
    <div class="container py-4" style="max-width: 600px;">
        <h2 class="fw-bold mb-1">My Staff Profile</h2>
        <p class="text-muted small mb-4">View and update your guide contact information</p>

        <div v-if="success" class="alert alert-success py-2 small alert-dismissible">
            {{ success }}
            <button type="button" class="btn-close btn-sm" @click="success = ''"></button>
        </div>
        <div v-if="error" class="alert alert-danger py-2 small alert-dismissible">
            {{ error }}
            <button type="button" class="btn-close btn-sm" @click="error = ''"></button>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else class="card p-4 shadow-sm border-0">
            <form @submit.prevent="saveProfile">
                <div class="mb-3">
                    <label class="form-label fw-semibold">Full Name</label>
                    <input v-model="profile.name" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                    <label class="form-label fw-semibold">Email Address</label>
                    <input v-model="profile.email" type="email" class="form-control bg-light" disabled />
                    <div class="form-text small">Email cannot be modified directly. Contact Admin for changes.</div>
                </div>
                <div class="mb-3">
                    <label class="form-label fw-semibold">Phone Number</label>
                    <input v-model="profile.phone_number" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                    <label class="form-label fw-semibold">Specialization</label>
                    <input v-model="profile.specialization" type="text" class="form-control" placeholder="e.g. First Aid, High Altitude Trekking" />
                </div>
                <div class="mb-3">
                    <label class="form-label fw-semibold">Staff Status</label>
                    <div>
                        <span class="badge" :class="profile.status === 'active' ? 'bg-success' : 'bg-danger'">
                            {{ profile.status }}
                        </span>
                    </div>
                </div>

                <button type="submit" class="btn btn-primary w-100 py-2 mt-2">Save Profile Changes</button>
            </form>
        </div>
    </div>
</template>
