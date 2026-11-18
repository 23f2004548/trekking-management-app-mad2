<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const staffList = ref([])
const loading = ref(true)
const showModal = ref(false)
const error = ref("")
const success = ref("")

const form = ref({
    name: "",
    username: "",
    email: "",
    password: "Staff123",
    phone_number: "",
    specialization: ""
})

async function fetchStaff() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/admin/staff`, {
            headers: { Authorization: "Bearer " + token }
        })
        staffList.value = res.data
    } catch (err) {
        error.value = "Failed to load staff list"
    } finally {
        loading.value = false
    }
}

async function addStaff() {
    error.value = ""
    success.value = ""
    try {
        await axios.post(`${BASE_URL}/admin/staff`, form.value, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = "Staff member added successfully"
        showModal.value = false
        form.value = {
            name: "",
            username: "",
            email: "",
            password: "Staff123",
            phone_number: "",
            specialization: ""
        }
        fetchStaff()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to add staff"
    }
}

async function toggleStaffStatus(id) {
    try {
        await axios.post(`${BASE_URL}/admin/staff/${id}/toggle-status`, {}, {
            headers: { Authorization: "Bearer " + token }
        })
        fetchStaff()
    } catch (err) {
        alert("Failed to update staff status")
    }
}

async function deleteStaff(id) {
    if (!confirm("Are you sure you want to delete this staff member? This will also remove their user account.")) return
    try {
        await axios.delete(`${BASE_URL}/admin/staff/${id}`, {
            headers: { Authorization: "Bearer " + token }
        })
        fetchStaff()
    } catch (err) {
        alert("Failed to delete staff member")
    }
}

onMounted(() => {
    fetchStaff()
})
</script>

<template>
    <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
            <div>
                <h2 class="fw-bold mb-0">Trek Staff Management</h2>
                <p class="text-muted small mb-0">Create guides and manage staff authorization</p>
            </div>
            <button class="btn btn-primary" @click="showModal = true">+ Add Staff Member</button>
        </div>

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

        <div v-else class="card shadow-sm border-0">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>#</th>
                            <th>Staff Name</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Specialization</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="s in staffList" :key="s.id">
                            <td>{{ s.id }}</td>
                            <td class="fw-semibold">{{ s.name }}</td>
                            <td>{{ s.email }}</td>
                            <td>{{ s.phone_number }}</td>
                            <td>{{ s.specialization || 'General' }}</td>
                            <td>
                                <span class="badge text-uppercase" :class="s.status === 'active' ? 'bg-success' : (s.status === 'pending' ? 'bg-warning text-dark' : 'bg-danger')">
                                    {{ s.status === 'pending' ? 'Pending Approval' : s.status }}
                                </span>
                            </td>
                            <td>
                                <button
                                    class="btn btn-sm me-2"
                                    :class="s.status === 'pending' ? 'btn-success' : (s.status === 'active' ? 'btn-outline-warning' : 'btn-outline-success')"
                                    @click="toggleStaffStatus(s.id)"
                                >
                                    {{ s.status === 'pending' ? '✓ Approve' : (s.status === 'active' ? 'Blacklist' : 'Activate') }}
                                </button>
                                <button class="btn btn-sm btn-outline-danger" @click="deleteStaff(s.id)">Delete</button>
                            </td>
                        </tr>
                        <tr v-if="staffList.length === 0">
                            <td colspan="7" class="text-center text-muted py-3">No staff members created yet</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Add Staff Modal -->
        <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">Add Trek Staff</h5>
                        <button type="button" class="btn-close" @click="showModal = false"></button>
                    </div>
                    <form @submit.prevent="addStaff">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Full Name</label>
                                <input v-model="form.name" type="text" class="form-control" required />
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Username</label>
                                <input v-model="form.username" type="text" class="form-control" required />
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Email</label>
                                <input v-model="form.email" type="email" class="form-control" required />
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Password</label>
                                <input v-model="form.password" type="password" class="form-control" required />
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Phone Number</label>
                                <input v-model="form.phone_number" type="text" class="form-control" placeholder="10-digit number" />
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Specialization</label>
                                <input v-model="form.specialization" type="text" class="form-control" placeholder="e.g. High Altitude, Rescue" />
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showModal = false">Cancel</button>
                            <button type="submit" class="btn btn-primary">Create Staff Account</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>
