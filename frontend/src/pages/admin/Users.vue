<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const users = ref([])
const loading = ref(true)
const error = ref("")
const success = ref("")

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
    error.value = ""
    success.value = ""
    try {
        const res = await axios.post(`${BASE_URL}/admin/users/${id}/toggle-active`, {}, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = res.data.message || "User status updated successfully."
        fetchUsers()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to update user status"
    }
}

async function deleteUser(id) {
    if (!confirm("Are you sure you want to delete this user?")) return
    error.value = ""
    success.value = ""
    try {
        const res = await axios.delete(`${BASE_URL}/admin/users/${id}`, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = res.data.message || "User deleted successfully."
        fetchUsers()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to delete user"
    }
}

onMounted(() => {
    fetchUsers()
})
</script>

<template>
    <div class="container py-4">
        <div v-if="success" class="alert py-2 px-3 small border-0 mb-3" style="background-color: #d1f4ff; color: #055160;">
            {{ success }}
        </div>
        <div v-if="error" class="alert alert-danger py-2 px-3 small border-0 mb-3">
            {{ error }}
        </div>

        <div class="d-flex justify-content-between align-items-center mb-3">
            <h3 class="fw-bold mb-0">Users</h3>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else class="card shadow-sm border">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light border-bottom">
                        <tr>
                            <th class="ps-3">ID</th>
                            <th>Full Name</th>
                            <th>Email</th>
                            <th>Registration Date</th>
                            <th>Status</th>
                            <th class="text-center pe-3">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="u in users" :key="u.id">
                            <td class="ps-3">{{ u.id }}</td>
                            <td class="fw-semibold">{{ u.name }}</td>
                            <td>{{ u.email }}</td>
                            <td>{{ u.created_at || '—' }}</td>
                            <td>
                                <span
                                    class="badge rounded-pill px-3 py-1"
                                    :class="u.is_active ? 'bg-primary' : 'bg-danger'"
                                >
                                    {{ u.is_active ? 'Active' : 'Blocked' }}
                                </span>
                            </td>
                            <td class="text-center pe-3">
                                <button
                                    class="btn btn-sm px-2 py-1 me-2"
                                    :class="u.is_active ? 'btn-outline-warning' : 'btn-outline-success'"
                                    :title="u.is_active ? 'Deactivate User' : 'Activate User'"
                                    @click="toggleUserActive(u.id)"
                                >
                                    <i class="bi" :class="u.is_active ? 'bi-slash-circle' : 'bi-check-circle'"></i>
                                </button>
                                <button
                                    class="btn btn-sm btn-outline-danger px-2 py-1"
                                    title="Delete User"
                                    @click="deleteUser(u.id)"
                                >
                                    <i class="bi bi-trash"></i>
                                </button>
                            </td>
                        </tr>
                        <tr v-if="users.length === 0">
                            <td colspan="6" class="text-center text-muted py-4">No users found</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
