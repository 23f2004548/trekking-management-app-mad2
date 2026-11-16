<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"

const router = useRouter()
const BASE_URL = "http://localhost:5000"

const username = ref("")
const password = ref("")
const error = ref("")
const loading = ref(false)

async function login() {
    error.value = ""
    loading.value = true
    try {
        const postdata = {
            username: username.value,
            password: password.value
        }
        const res = await axios.post(BASE_URL + '/login', postdata)
        if (res.status === 200) {
            localStorage.setItem("token", res.data.access_token)
            localStorage.setItem("role", res.data.role)
            
            // Redirect users to role-specific dashboards
            if (res.data.role === 'admin') {
                router.push('/admin/dashboard')
            } else if (res.data.role === 'staff') {
                router.push('/staff/dashboard')
            } else if (res.data.role === 'user') {
                router.push('/user/dashboard')
            }
        }
    } catch (err) {
        error.value = err.response?.data?.message || "Invalid username or password"
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="container py-5 d-flex justify-content-center">
        <div class="card p-4 auth-card" style="width: 100%; max-width: 440px;">
            <h3 class="text-center fw-bold mb-1">Sign In</h3>
            <p class="text-muted text-center small mb-4">Trekking Management Portal</p>
            
            <form @submit.prevent="login">
                <div class="mb-3">
                    <label for="username" class="form-label fw-semibold">Username or Email</label>
                    <input type="text" class="form-control" id="username" v-model="username" placeholder="admin@gmail.com" required />
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label fw-semibold">Password</label>
                    <input type="password" class="form-control" id="password" v-model="password" placeholder="••••••••" required />
                </div>
                
                <button type="submit" class="btn btn-primary w-100 py-2 mt-2" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    Sign In
                </button>
                
                <div v-if="error" class="alert alert-danger mt-3 py-2 small">{{ error }}</div>
            </form>
            
            <p class="text-center mt-4 small mb-0">
                Are you a new trekker? 
                <a @click.prevent="router.push('/register')" href="#" class="text-primary text-decoration-none fw-semibold">Register here</a>
            </p>
        </div>
    </div>
</template>
