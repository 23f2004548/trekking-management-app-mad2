<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const bookings = ref([])
const loading = ref(true)
const error = ref("")
const success = ref("")
const statusFilter = ref("all")
const searchTerm = ref("")

async function fetchBookings() {
    loading.value = true
    try {
        const params = new URLSearchParams()
        if (statusFilter.value !== "all") params.append("status", statusFilter.value)
        if (searchTerm.value.trim()) params.append("search", searchTerm.value.trim())

        const res = await axios.get(`${BASE_URL}/admin/bookings?${params.toString()}`, {
            headers: { Authorization: "Bearer " + token }
        })
        bookings.value = res.data
    } catch (err) {
        error.value = "Failed to load bookings"
    } finally {
        loading.value = false
    }
}

async function updateStatus(id, newStatus) {
    error.value = ""
    success.value = ""
    try {
        await axios.post(`${BASE_URL}/admin/bookings/${id}/status`, { status: newStatus }, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = "Booking status updated successfully"
        fetchBookings()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to update status"
    }
}

function filterBy(status) {
    statusFilter.value = status
    fetchBookings()
}

function getBadge(status) {
    if (status === "Booked") return "bg-primary"
    if (status === "Completed") return "bg-success"
    if (status === "Cancelled") return "bg-danger"
    return "bg-secondary"
}

onMounted(() => {
    fetchBookings()
})
</script>

<template>
    <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold mb-0">Booking Records & History</h2>
                <p class="text-muted small mb-0">View all user bookings, track status progression, and manage expedition records</p>
            </div>
        </div>

        <!-- Filter bar -->
        <div class="card shadow-sm border-0 mb-4 bg-white">
            <div class="card-body p-3">
                <div class="row g-2 align-items-center">
                    <div class="col-md-6 d-flex gap-2">
                        <button
                            class="btn btn-sm"
                            :class="statusFilter === 'all' ? 'btn-dark' : 'btn-outline-secondary'"
                            @click="filterBy('all')"
                        >
                            All ({{ bookings.length }})
                        </button>
                        <button
                            class="btn btn-sm"
                            :class="statusFilter === 'Booked' ? 'btn-primary' : 'btn-outline-secondary'"
                            @click="filterBy('Booked')"
                        >
                            Booked
                        </button>
                        <button
                            class="btn btn-sm"
                            :class="statusFilter === 'Completed' ? 'btn-success' : 'btn-outline-secondary'"
                            @click="filterBy('Completed')"
                        >
                            Completed
                        </button>
                        <button
                            class="btn btn-sm"
                            :class="statusFilter === 'Cancelled' ? 'btn-danger' : 'btn-outline-secondary'"
                            @click="filterBy('Cancelled')"
                        >
                            Cancelled
                        </button>
                    </div>
                    <div class="col-md-6">
                        <form @submit.prevent="fetchBookings" class="d-flex gap-2">
                            <input
                                type="text"
                                v-model="searchTerm"
                                class="form-control form-control-sm"
                                placeholder="Search by trekker name, email, or trek route..."
                            />
                            <button type="submit" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-search"></i>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
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
                            <th>Trekker</th>
                            <th>Email</th>
                            <th>Trek Route</th>
                            <th>Location</th>
                            <th>Trek Dates</th>
                            <th>Booked On</th>
                            <th>Status</th>
                            <th>Change Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="b in bookings" :key="b.id">
                            <td>{{ b.id }}</td>
                            <td class="fw-semibold">{{ b.user_name || '—' }}</td>
                            <td>{{ b.user_email || '—' }}</td>
                            <td class="fw-semibold">{{ b.trek_name || '—' }}</td>
                            <td>{{ b.trek_location || '—' }}</td>
                            <td class="small">{{ b.trek_start_date }} → {{ b.trek_end_date }}</td>
                            <td class="small">{{ b.booking_date }}</td>
                            <td>
                                <span class="badge" :class="getBadge(b.status)">{{ b.status }}</span>
                            </td>
                            <td>
                                <select
                                    class="form-select form-select-sm"
                                    style="width: 130px;"
                                    :value="b.status"
                                    @change="updateStatus(b.id, $event.target.value)"
                                >
                                    <option>Pending</option>
                                    <option>Booked</option>
                                    <option>Completed</option>
                                    <option>Cancelled</option>
                                </select>
                            </td>
                        </tr>
                        <tr v-if="bookings.length === 0">
                            <td colspan="9" class="text-center text-muted py-3">No booking records found</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
