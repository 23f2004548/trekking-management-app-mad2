<script setup>
import { ref, computed, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const staffList = ref([])
const loading = ref(true)
const showModal = ref(false)
const error = ref("")
const success = ref("")
const currentTab = ref("all")

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

const filteredStaff = computed(() => {
    if (currentTab.value === "all") return staffList.value
    return staffList.value.filter(s => s.status?.toLowerCase() === currentTab.value)
})

function countByStatus(status) {
    return staffList.value.filter(s => s.status?.toLowerCase() === status).length
}

async function addStaff() {
    error.value = ""
    success.value = ""
    try {
        await axios.post(`${BASE_URL}/admin/staff`, form.value, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = "Staff member created successfully."
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

async function setStaffStatus(id, newStatus) {
    error.value = ""
    success.value = ""
    try {
        const res = await axios.post(`${BASE_URL}/admin/staff/${id}/toggle-status`, { status: newStatus }, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = res.data.message || `Staff status updated to ${newStatus}.`
        fetchStaff()
    } catch (err) {
        error.value = "Failed to update staff status"
    }
}

async function deleteStaff(id) {
    if (!confirm("Are you sure you want to delete this staff member? This will also remove their user account.")) return
    error.value = ""
    success.value = ""
    try {
        const res = await axios.delete(`${BASE_URL}/admin/staff/${id}`, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = res.data.message || "Staff member deleted successfully."
        fetchStaff()
    } catch (err) {
        error.value = "Failed to delete staff member"
    }
}

onMounted(() => {
    fetchStaff()
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
            <h3 class="fw-bold mb-0">Staff</h3>
            <button class="btn btn-primary btn-sm px-3" @click="showModal = true">+ Add Staff Member</button>
        </div>

        <ul class="nav nav-tabs mb-3">
            <li class="nav-item">
                <button
                    class="nav-link"
                    :class="{ active: currentTab === 'all' }"
                    @click="currentTab = 'all'"
                >
                    All ({{ staffList.length }})
                </button>
            </li>
            <li class="nav-item">
                <button
                    class="nav-link"
                    :class="{ active: currentTab === 'pending' }"
                    @click="currentTab = 'pending'"
                >
                    Pending ({{ countByStatus('pending') }})
                </button>
            </li>
            <li class="nav-item">
                <button
                    class="nav-link"
                    :class="{ active: currentTab === 'approved' }"
                    @click="currentTab = 'approved'"
                >
                    Approved ({{ countByStatus('approved') }})
                </button>
            </li>
            <li class="nav-item">
                <button
                    class="nav-link"
                    :class="{ active: currentTab === 'blacklisted' }"
                    @click="currentTab = 'blacklisted'"
                >
                    Blacklisted ({{ countByStatus('blacklisted') }})
                </button>
            </li>
        </ul>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else class="card shadow-sm border">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light border-bottom">
                        <tr>
                            <th class="ps-3">ID</th>
                            <th>Staff Name</th>
                            <th>Email</th>
                            <th>Contact</th>
                            <th>Specialization</th>
                            <th>Status</th>
                            <th class="text-center pe-3">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="s in filteredStaff" :key="s.id">
                            <td class="ps-3">{{ s.id }}</td>
                            <td class="fw-semibold">{{ s.name }}</td>
                            <td>{{ s.email }}</td>
                            <td>{{ s.phone_number }}</td>
                            <td>{{ s.specialization || 'General' }}</td>
                            <td>
                                <span
                                    class="badge rounded-pill px-3 py-1"
                                    :class="s.status?.toLowerCase() === 'approved' ? 'bg-success' : (s.status?.toLowerCase() === 'pending' ? 'bg-warning text-dark' : 'bg-danger')"
                                >
                                    {{ s.status?.toLowerCase() === 'pending' ? 'Pending' : (s.status?.toLowerCase() === 'approved' ? 'Approved' : 'Blacklisted') }}
                                </span>
                            </td>
                            <td class="text-center pe-3">
                                <template v-if="s.status?.toLowerCase() === 'pending'">
                                    <button
                                        class="btn btn-sm btn-success px-2 py-1 me-1"
                                        title="Approve Staff"
                                        @click="setStaffStatus(s.id, 'approved')"
                                    >
                                        Approve
                                    </button>
                                    <button
                                        class="btn btn-sm btn-danger px-2 py-1 me-1"
                                        title="Reject / Blacklist"
                                        @click="setStaffStatus(s.id, 'blacklisted')"
                                    >
                                        Reject
                                    </button>
                                </template>
                                <template v-else-if="s.status?.toLowerCase() === 'approved'">
                                    <button
                                        class="btn btn-sm btn-outline-warning px-2 py-1 me-1"
                                        title="Blacklist Staff"
                                        @click="setStaffStatus(s.id, 'blacklisted')"
                                    >
                                        <i class="bi bi-slash-circle"></i>
                                    </button>
                                </template>
                                <template v-else>
                                    <button
                                        class="btn btn-sm btn-outline-success px-2 py-1 me-1"
                                        title="Approve Staff"
                                        @click="setStaffStatus(s.id, 'approved')"
                                    >
                                        <i class="bi bi-check-circle"></i>
                                    </button>
                                </template>

                                <button
                                    class="btn btn-outline-secondary btn-sm px-2 py-1"
                                    title="Delete Staff"
                                    @click="deleteStaff(s.id)"
                                >
                                    <i class="bi bi-trash text-danger"></i>
                                </button>
                            </td>
                        </tr>
                        <tr v-if="filteredStaff.length === 0">
                            <td colspan="7" class="text-center text-muted py-4">No staff members found</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

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
