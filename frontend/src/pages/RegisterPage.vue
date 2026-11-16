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
const confirmPassword = ref("")
const error = ref("")
const success = ref("")
const loading = ref(false)

async function register() {
    error.value = ""
    success.value = ""

    if (password.value !== confirmPassword.value) {
        error.value = "Passwords do not match"
        return
    }

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
            success.value = "Registered successfully! Redirecting to login..."
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
    <div class="auth-page min-vh-100">
        <div class="page-header">Trekking Management Application</div>

        <div class="container register-wrap d-flex align-items-center justify-content-center py-4">
            <div class="card register-card shadow-sm">
                <div class="card-body p-4 p-md-5">
                    <h3 class="text-center fw-bold mb-4">Register</h3>

                    <div v-if="success" class="alert alert-success py-2 small">{{ success }}</div>
                    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>

                    <form @submit.prevent="register">
                        <div class="mb-3">
                            <input v-model="name" type="text" class="form-control" placeholder="Full Name" required />
                        </div>

                        <div class="mb-3">
                            <input v-model="username" type="text" class="form-control" placeholder="Username" required />
                        </div>

                        <div class="mb-3">
                            <input v-model="email" type="email" class="form-control" placeholder="Email" required />
                        </div>

                        <div class="mb-3">
                            <input v-model="password" type="password" class="form-control" placeholder="Password (min 6 chars)" minlength="6" required />
                        </div>

                        <div class="mb-3">
                            <input v-model="confirmPassword" type="password" class="form-control" placeholder="Confirm Password" minlength="6" required />
                        </div>

                        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                            <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                            Register
                        </button>

                        <p class="text-center mt-3 mb-0 small">
                            Already have an account? 
                            <a @click.prevent="router.push('/login')" href="#" class="text-primary text-decoration-none fw-semibold">Login here</a>
                        </p>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>
