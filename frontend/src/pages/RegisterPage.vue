<script setup>
import { ref } from "vue"
import axios from "axios"
import { useRouter } from "vue-router"

const router = useRouter()
const BASE_URL = "http://localhost:5000"

const name = ref("")
const email = ref("")
const username = ref("")
const password = ref("")
const error = ref("")
const success = ref("")
const loading = ref(false)

async function register() {
    error.value = ""
    success.value = ""
    loading.value = true
    try {
        const postdata = {
            name: name.value,
            email: email.value,
            username: username.value,
            password: password.value,
            role: "user"
        }

        const res = await axios.post(BASE_URL + "/register", postdata)
        if (res.status === 201) {
            success.value = "Registration successful! Redirecting to login..."
            setTimeout(() => {
                router.push("/login")
            }, 1200)
        }
    } catch (err) {
        error.value = err.response?.data?.message || "Registration failed"
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="container py-5 d-flex justify-content-center">
        <div class="card p-4 auth-card" style="width: 100%; max-width: 480px;">
            <h3 class="text-center fw-bold mb-1">Trekker Registration</h3>
            <p class="text-muted text-center small mb-4">Create your account to book and track treks</p>

            <div v-if="success" class="alert alert-success py-2 small">{{ success }}</div>
            <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>

            <form @submit.prevent="register">
                <div class="mb-3">
                    <label class="form-label fw-semibold">Full Name</label>
                    <input v-model="name" type="text" class="form-control" placeholder="John Doe" required />
                </div>
                <div class="mb-3">
                    <label class="form-label fw-semibold">Username</label>
                    <input v-model="username" type="text" class="form-control" placeholder="johndoe" required />
                </div>
                <div class="mb-3">
                    <label class="form-label fw-semibold">Email</label>
                    <input v-model="email" type="email" class="form-control" placeholder="john@example.com" required />
                </div>
                <div class="mb-3">
                    <label class="form-label fw-semibold">Password</label>
                    <input v-model="password" type="password" class="form-control" placeholder="Minimum 6 characters" required />
                </div>

                <button type="submit" class="btn btn-primary w-100 py-2 mt-2" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    Register
                </button>

                <p class="text-center mt-3 text-muted small mb-0">
                    Already have an account?
                    <button type="button" @click="router.push('/login')" class="btn btn-link p-0 small align-baseline">Sign in</button>
                </p>
            </form>
        </div>
    </div>
</template>
