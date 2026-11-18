<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"

function getToken() {
    return localStorage.getItem("token")
}

const bookings = ref([])
const loading = ref(true)
const error = ref("")
const success = ref("")

const showCancelModal = ref(false)
const cancelingBooking = ref(null)

async function fetchBookings() {
    loading.value = true
    error.value = ""
    try {
        const res = await axios.get(`${BASE_URL}/user/bookings`, {
            headers: { Authorization: "Bearer " + getToken() }
        })
        bookings.value = res.data.bookings || []
    } catch (err) {
        if (err.response?.status === 401) {
            error.value = "Session expired. Please log in again."
        } else {
            error.value = err.response?.data?.message || "Failed to load bookings"
        }
    } finally {
        loading.value = false
    }
}

function promptCancel(booking) {
    cancelingBooking.value = booking
    showCancelModal.value = true
}

async function confirmCancel() {
    if (!cancelingBooking.value) return
    error.value = ""
    success.value = ""
    try {
        const res = await axios.post(`${BASE_URL}/user/bookings/${cancelingBooking.value.id}/cancel`, {}, {
            headers: { Authorization: "Bearer " + getToken() }
        })
        success.value = res.data.message || "Booking cancelled successfully"
        showCancelModal.value = false
        cancelingBooking.value = null
        fetchBookings()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to cancel booking"
        showCancelModal.value = false
    }
}

onMounted(() => {
    fetchBookings()
})
</script>

<template>
    <div class="container py-4">
        <!-- Notification alert -->
        <div v-if="success" class="alert py-2 px-3 small border-0 mb-3" style="background-color: #d1f4ff; color: #055160;">
            {{ success }}
        </div>
        <div v-if="error" class="alert alert-danger py-2 px-3 small border-0 mb-3">
            {{ error }}
        </div>

        <h3 class="fw-bold mb-3">My Bookings</h3>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <!-- Bookings Card matching screenshot exactly -->
        <div v-else class="card shadow-sm border">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light border-bottom">
                        <tr>
                            <th class="ps-3">Trek Name</th>
                            <th>Location</th>
                            <th>Booking Date</th>
                            <th>Start Date</th>
                            <th>End Date</th>
                            <th>Status</th>
                            <th>Action</th>
                            <th class="pe-3">Staff</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="b in bookings" :key="b.id">
                            <td class="ps-3 fw-semibold">{{ b.trek_name }}</td>
                            <td>{{ b.trek_location }}</td>
                            <td>{{ b.booking_date }}</td>
                            <td>{{ b.trek_start_date }}</td>
                            <td>{{ b.trek_end_date }}</td>
                            <td>
                                <span
                                    class="badge rounded-pill px-3 py-1"
                                    :class="b.status?.toLowerCase() === 'confirmed' ? 'bg-success' : (b.status?.toLowerCase() === 'cancelled' ? 'bg-danger' : 'bg-warning text-dark')"
                                >
                                    {{ b.status?.toLowerCase() === 'confirmed' ? 'Confirmed' : (b.status?.toLowerCase() === 'cancelled' ? 'Cancelled' : 'Pending') }}
                                </span>
                            </td>
                            <td>
                                <button
                                    v-if="b.status?.toLowerCase() !== 'cancelled'"
                                    class="btn btn-danger btn-sm px-3 py-1"
                                    @click="promptCancel(b)"
                                >
                                    Cancel Booking
                                </button>
                                <span v-else class="text-muted small">Cancelled</span>
                            </td>
                            <td class="pe-3">{{ b.staff_name || 'N/A' }}</td>
                        </tr>
                        <tr v-if="bookings.length === 0">
                            <td colspan="8" class="text-center text-muted py-4">You have no bookings yet.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Cancel Confirmation Modal -->
        <div v-if="showCancelModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold text-danger">Cancel Booking</h5>
                        <button type="button" class="btn-close" @click="showCancelModal = false"></button>
                    </div>
                    <div class="modal-body" v-if="cancelingBooking">
                        <p>Are you sure you want to cancel your booking for <strong>{{ cancelingBooking.trek_name }}</strong>?</p>
                        <p class="text-muted small mb-0">Your slot will be released back to the available pool for other trekkers.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" @click="showCancelModal = false">Keep Booking</button>
                        <button type="button" class="btn btn-danger" @click="confirmCancel">Confirm Cancellation</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
