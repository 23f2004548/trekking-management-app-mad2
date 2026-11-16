<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const bookings = ref([])
const loading = ref(true)
const error = ref("")
const success = ref("")

async function fetchBookings() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/admin/bookings`, {
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
                <p class="text-muted small mb-0">View all user bookings and manage expedition participation</p>
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
