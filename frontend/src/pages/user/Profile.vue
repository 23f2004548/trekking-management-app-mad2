<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const user = ref({
    name: "",
    email: "",
    role: "user"
})
const password = ref("")
const loading = ref(true)
const saving = ref(false)
const error = ref("")
const success = ref("")

async function fetchProfile() {
    loading.value = true
    error.value = ""
    try {
        const res = await axios.get(`${BASE_URL}/user/profile`, {
            headers: { Authorization: "Bearer " + token }
        })
        user.value = res.data.user
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to load profile"
    } finally {
        loading.value = false
    }
}

async function saveProfile() {
    saving.value = true
    error.value = ""
    success.value = ""
    try {
        const payload = {
            name: user.value.name,
            email: user.value.email
        }
        if (password.value) {
            payload.password = password.value
        }

        const res = await axios.put(`${BASE_URL}/user/profile`, payload, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = res.data.message || "Profile updated successfully"
        localStorage.setItem("user_name", user.value.name)
        password.value = ""
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to update profile"
    } finally {
        saving.value = false
    }
}

onMounted(() => {
    fetchProfile()
})
</script>

<template>
    <div>
        <h4 class="fw-bold mb-3">Profile</h4>

        <!-- Alerts -->
        <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="bi bi-check-circle-fill me-2"></i>{{ success }}
            <button type="button" class="btn-close" @click="success = ''"></button>
        </div>
        <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ error }}
            <button type="button" class="btn-close" @click="error = ''"></button>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <!-- Profile Card matching MAD 1 user_profile.html -->
        <div v-else class="card shadow-sm border-0 bg-white">
            <div class="card-body p-4">
                <form @submit.prevent="saveProfile">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Full Name</label>
                            <input
                                type="text"
                                v-model="user.name"
                                class="form-control"
                                required
                            />
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Email Address</label>
                            <input
                                type="email"
                                v-model="user.email"
                                class="form-control"
                                required
                            />
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Role</label>
                            <input
                                type="text"
                                class="form-control bg-light"
                                :value="(user.role || 'user').toUpperCase()"
                                readonly
                                disabled
                            />
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-semibold">New Password (optional)</label>
                            <input
                                type="password"
                                v-model="password"
                                class="form-control"
                                placeholder="Leave blank to keep current password"
                            />
                        </div>
                    </div>

                    <div class="d-flex justify-content-end gap-2 mt-4">
                        <button
                            type="button"
                            class="btn btn-outline-secondary px-4"
                            @click="router.push('/user/dashboard')"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            class="btn btn-primary px-4"
                            :disabled="saving"
                        >
                            <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                            Save Changes
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>
