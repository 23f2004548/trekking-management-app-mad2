<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"

const router = useRouter()
const BASE_URL = "http://localhost:5000"

const email = ref("")
const password = ref("")
const error = ref("")
const loading = ref(false)

async function login() {
    error.value = ""
    loading.value = true
    try {
        const postdata = {
            username: email.value,
            password: password.value
        }
        const res = await axios.post(BASE_URL + '/login', postdata)
        if (res.status === 200) {
            localStorage.setItem("token", res.data.access_token)
            localStorage.setItem("role", res.data.role)
            localStorage.setItem("user_name", res.data.user?.name || "User")
            
            // Role-specific redirect
            if (res.data.role === 'admin') {
                router.push('/admin/dashboard')
            } else if (res.data.role === 'staff') {
                router.push('/staff/dashboard')
            } else if (res.data.role === 'user') {
                router.push('/user/dashboard')
            }
        }
    } catch (err) {
        error.value = err.response?.data?.message || "Invalid credentials"
    } finally {
        loading.value = false
    }
}

function resetForm() {
    email.value = ""
    password.value = ""
    error.value = ""
}
</script>

<template>
    <div class="auth-page min-vh-100">
        <div class="page-header">Trekking Management Application</div>

        <div class="container login-wrap d-flex align-items-center justify-content-center py-4">
            <div class="card login-card shadow-sm">
                <div class="card-body p-4 p-md-5">
                    <h3 class="text-center fw-bold mb-4">Login</h3>

                    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>

                    <form @submit.prevent="login">
                        <div class="mb-3">
                            <input
                                v-model="email"
                                type="text"
                                class="form-control"
                                placeholder="Email or Username"
                                required
                            />
                        </div>

                        <div class="mb-3">
                            <input
                                v-model="password"
                                type="password"
                                class="form-control"
                                placeholder="Password"
                                required
                            />
                        </div>

                        <div class="form-check mb-3">
                            <input class="form-check-input" type="checkbox" id="rememberMe">
                            <label class="form-check-label small" for="rememberMe">Remember me</label>
                        </div>

                        <div class="d-grid gap-2 d-flex justify-content-between">
                            <button type="submit" class="btn btn-primary px-4" :disabled="loading">
                                <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                                Login
                            </button>
                            <button type="button" class="btn btn-danger px-4" @click="resetForm">Reset</button>
                        </div>

                        <p class="text-center mt-4 mb-0 small">
                            Don't have an account? 
                            <a @click.prevent="router.push('/register')" href="#" class="text-primary text-decoration-none fw-semibold">Register here</a>
                        </p>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>
