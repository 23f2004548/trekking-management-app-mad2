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
        success.value = "Booking status updated successfully."
        fetchBookings()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to update status"
    }
}

function filterBy(status) {
    statusFilter.value = status
    fetchBookings()
}

onMounted(() => {
    fetchBookings()
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
            <h3 class="fw-bold mb-0">Bookings</h3>
        </div>

        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
            <ul class="nav nav-tabs">
                <li class="nav-item">
                    <button
                        class="nav-link"
                        :class="{ active: statusFilter === 'all' }"
                        @click="filterBy('all')"
                    >
                        All ({{ bookings.length }})
                    </button>
                </li>
                <li class="nav-item">
                    <button
                        class="nav-link"
                        :class="{ active: statusFilter === 'confirmed' }"
                        @click="filterBy('confirmed')"
                    >
                        Confirmed
                    </button>
                </li>
                <li class="nav-item">
                    <button
                        class="nav-link"
                        :class="{ active: statusFilter === 'pending' }"
                        @click="filterBy('pending')"
                    >
                        Pending
                    </button>
                </li>
                <li class="nav-item">
                    <button
                        class="nav-link"
                        :class="{ active: statusFilter === 'cancelled' }"
                        @click="filterBy('cancelled')"
                    >
                        Cancelled
                    </button>
                </li>
            </ul>

            <form @submit.prevent="fetchBookings" class="d-flex gap-2">
                <input
                    type="text"
                    v-model="searchTerm"
                    class="form-control form-control-sm"
                    placeholder="Search by trekker, email, or trek..."
                    style="width: 250px;"
                />
                <button type="submit" class="btn btn-sm btn-primary">
                    <i class="bi bi-search"></i>
                </button>
            </form>
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
                            <th>User Name</th>
                            <th>Trek Name</th>
                            <th>Booking Date</th>
                            <th>Status</th>
                            <th class="text-center pe-3">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="b in bookings" :key="b.id">
                            <td class="ps-3">{{ b.id }}</td>
                            <td class="fw-semibold">{{ b.user_name || '—' }}</td>
                            <td>{{ b.trek_name || '—' }}</td>
                            <td>{{ b.booking_date }}</td>
                            <td>
                                <span
                                    class="badge rounded-pill px-3 py-1"
                                    :class="b.status?.toLowerCase() === 'confirmed' ? 'bg-success' : (b.status?.toLowerCase() === 'pending' ? 'bg-primary' : 'bg-danger')"
                                >
                                    {{ b.status?.toLowerCase() === 'confirmed' ? 'Confirmed' : (b.status?.toLowerCase() === 'pending' ? 'Pending' : 'Cancelled') }}
                                </span>
                            </td>
                            <td class="text-center pe-3">
                                <template v-if="b.status?.toLowerCase() === 'pending'">
                                    <button
                                        class="btn btn-sm btn-success px-2 py-1 me-1"
                                        title="Confirm Booking"
                                        @click="updateStatus(b.id, 'confirmed')"
                                    >
                                        Confirm
                                    </button>
                                    <button
                                        class="btn btn-sm btn-danger px-2 py-1"
                                        title="Cancel Booking"
                                        @click="updateStatus(b.id, 'cancelled')"
                                    >
                                        Cancel
                                    </button>
                                </template>
                                <template v-else-if="b.status?.toLowerCase() === 'confirmed'">
                                    <button
                                        class="btn btn-sm btn-danger px-2 py-1"
                                        title="Cancel Booking"
                                        @click="updateStatus(b.id, 'cancelled')"
                                    >
                                        Cancel
                                    </button>
                                </template>
                                <template v-else>
                                    <span class="text-muted small">None</span>
                                </template>
                            </td>
                        </tr>
                        <tr v-if="bookings.length === 0">
                            <td colspan="6" class="text-center text-muted py-4">No bookings found</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
