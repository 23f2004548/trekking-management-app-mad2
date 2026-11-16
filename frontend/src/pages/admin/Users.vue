<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const users = ref([])
const loading = ref(true)
const error = ref("")

async function fetchUsers() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/admin/users`, {
            headers: { Authorization: "Bearer " + token }
        })
        users.value = res.data
    } catch (err) {
        error.value = "Failed to load users"
    } finally {
        loading.value = false
    }
}

async function toggleUserActive(id) {
    try {
        await axios.post(`${BASE_URL}/admin/users/${id}/toggle-active`, {}, {
            headers: { Authorization: "Bearer " + token }
        })
        fetchUsers()
    } catch (err) {
        alert("Failed to update user status")
    }
}

async function deleteUser(id) {
    if (!confirm("Are you sure you want to delete this user?")) return
    try {
        await axios.delete(`${BASE_URL}/admin/users/${id}`, {
            headers: { Authorization: "Bearer " + token }
        })
        fetchUsers()
    } catch (err) {
        alert("Failed to delete user")
    }
}

onMounted(() => {
    fetchUsers()
})
</script>

<template>
    <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold mb-0">Registered Trekkers</h2>
                <p class="text-muted small mb-0">View registered users and manage active status</p>
            </div>
        </div>

        <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else class="card shadow-sm border-0">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>#</th>
                            <th>Name</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Joined</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="u in users" :key="u.id">
                            <td>{{ u.id }}</td>
                            <td class="fw-semibold">{{ u.name }}</td>
                            <td>{{ u.username }}</td>
                            <td>{{ u.email }}</td>
                            <td>{{ u.created_at || '—' }}</td>
                            <td>
                                <span class="badge" :class="u.is_active ? 'bg-success' : 'bg-secondary'">
                                    {{ u.is_active ? 'Active' : 'Deactivated' }}
                                </span>
                            </td>
                            <td>
                                <button
                                    class="btn btn-sm me-2"
                                    :class="u.is_active ? 'btn-outline-warning' : 'btn-outline-success'"
                                    @click="toggleUserActive(u.id)"
                                >
                                    {{ u.is_active ? 'Deactivate' : 'Activate' }}
                                </button>
                                <button class="btn btn-sm btn-outline-danger" @click="deleteUser(u.id)">Delete</button>
                            </td>
                        </tr>
                        <tr v-if="users.length === 0">
                            <td colspan="7" class="text-center text-muted py-3">No trekkers registered yet</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
