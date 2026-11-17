<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"

const router = useRouter()
const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

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
            headers: { Authorization: "Bearer " + token }
        })
        bookings.value = res.data.bookings || []
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to load bookings"
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
            headers: { Authorization: "Bearer " + token }
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
    <div>
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="fw-bold mb-0">My Bookings</h4>
            <button class="btn btn-primary btn-sm" @click="router.push('/user/browse')">
                <i class="bi bi-compass me-1"></i>Book New Trek
            </button>
        </div>

        <!-- Alert messages -->
        <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="bi bi-check-circle-fill me-2"></i>{{ success }}
            <button type="button" class="btn-close" @click="success = ''"></button>
        </div>
        <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ error }}
            <button type="button" class="btn-close" @click="error = ''"></button>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <!-- Bookings Card & Table matching MAD 1 user_bookings.html -->
        <div v-else class="card shadow-sm border-0 bg-white">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-bordered table-hover table-sm align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Trek Name</th>
                                <th>Location</th>
                                <th>Booking Date</th>
                                <th>Start Date</th>
                                <th>End Date</th>
                                <th>Status</th>
                                <th>Action</th>
                                <th>Staff</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="b in bookings" :key="b.id">
                                <td class="fw-semibold">{{ b.trek_name }}</td>
                                <td><i class="bi bi-geo-alt text-danger me-1"></i>{{ b.trek_location }}</td>
                                <td>{{ b.booking_date }}</td>
                                <td>{{ b.trek_start_date }}</td>
                                <td>{{ b.trek_end_date }}</td>
                                <td>
                                    <span v-if="b.status === 'Booked' || b.status === 'Confirmed'" class="badge bg-success">Confirmed</span>
                                    <span v-else-if="b.status === 'Cancelled'" class="badge bg-danger">Cancelled</span>
                                    <span v-else-if="b.status === 'Completed'" class="badge bg-primary">Completed</span>
                                    <span v-else class="badge bg-warning text-dark">Pending</span>
                                </td>
                                <td>
                                    <button
                                        v-if="b.status !== 'Cancelled' && b.status !== 'Completed'"
                                        class="btn btn-danger btn-sm"
                                        @click="promptCancel(b)"
                                    >
                                        Cancel Booking
                                    </button>
                                    <span v-else-if="b.status === 'Cancelled'" class="text-muted">Cancelled</span>
                                    <span v-else class="text-success small fw-semibold">
                                        <i class="bi bi-check2-all me-1"></i>Completed
                                    </span>
                                </td>
                                <td>{{ b.staff_name || 'Unassigned' }}</td>
                            </tr>
                            <tr v-if="bookings.length === 0">
                                <td colspan="8" class="text-center text-muted py-4">
                                    <i class="bi bi-journal-x fs-3 d-block mb-2"></i>
                                    You have no bookings yet. Explore our open treks in <router-link to="/user/browse">Browse Treks</router-link>!
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
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
