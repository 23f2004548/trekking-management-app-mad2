<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"

const router = useRouter()
const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const bookings = ref([])
const loading = ref(true)
const error = ref("")
const success = ref("")
const statusFilter = ref("all")

const showCancelModal = ref(false)
const cancelingBooking = ref(null)

const showTrackModal = ref(false)
const trackingBooking = ref(null)

const showPayModal = ref(false)
const payingBooking = ref(null)
const selectedPayMethod = ref("UPI")
const paymentProcessing = ref(false)

function openPaymentModal(booking) {
    payingBooking.value = booking
    selectedPayMethod.value = "UPI"
    showPayModal.value = true
}

async function processPaymentSimulation() {
    if (!payingBooking.value) return
    paymentProcessing.value = true
    error.value = ""
    success.value = ""
    try {
        const res = await axios.post(`${BASE_URL}/user/bookings/${payingBooking.value.id}/pay`, {
            method: selectedPayMethod.value
        }, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = res.data.message || "Payment processed successfully!"
        showPayModal.value = false
        payingBooking.value = null
        fetchBookings()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to process payment"
    } finally {
        paymentProcessing.value = false
    }
}

async function fetchBookings() {
    loading.value = true
    error.value = ""
    try {
        const url = statusFilter.value === "all"
            ? `${BASE_URL}/user/bookings`
            : `${BASE_URL}/user/bookings?status=${statusFilter.value}`
        const res = await axios.get(url, {
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

function openTracker(booking) {
    trackingBooking.value = booking
    showTrackModal.value = true
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

function filterBy(status) {
    statusFilter.value = status
    fetchBookings()
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

        <!-- Filter tabs matching TrekFlow design -->
        <div class="d-flex gap-2 mb-3">
            <button
                class="btn btn-sm"
                :class="statusFilter === 'all' ? 'btn-dark' : 'btn-outline-secondary'"
                @click="filterBy('all')"
            >
                All Bookings
            </button>
            <button
                class="btn btn-sm"
                :class="statusFilter === 'Booked' ? 'btn-success' : 'btn-outline-secondary'"
                @click="filterBy('Booked')"
            >
                Active / Confirmed
            </button>
            <button
                class="btn btn-sm"
                :class="statusFilter === 'Completed' ? 'btn-primary' : 'btn-outline-secondary'"
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

        <!-- Bookings Card & Table matching MAD 1 user_bookings.html with Milestone 6 enhancements -->
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
                                <th>Payment</th>
                                <th>Trek Progress</th>
                                <th>Action</th>
                                <th>Staff</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="b in bookings" :key="b.id">
                                <td class="fw-semibold">
                                    <span class="text-dark">{{ b.trek_name }}</span>
                                    <span class="d-block small text-muted">₹{{ b.trek_price }} · {{ b.trek_difficulty }}</span>
                                </td>
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
                                    <!-- Enhancement 2: Payment Simulation -->
                                    <span v-if="b.payment_status === 'Paid'" class="badge bg-success">
                                        <i class="bi bi-check2-circle me-1"></i>Paid
                                    </span>
                                    <button
                                        v-else-if="b.status !== 'Cancelled'"
                                        class="btn btn-warning btn-sm fw-semibold text-dark py-0 px-2"
                                        @click="openPaymentModal(b)"
                                    >
                                        <i class="bi bi-credit-card me-1"></i>Pay ₹{{ b.trek_price }}
                                    </button>
                                    <span v-else class="text-muted small">N/A</span>
                                </td>
                                <td>
                                    <!-- Milestone 6: Live Trek Tracking Badge & Trigger -->
                                    <button
                                        class="btn btn-outline-primary btn-sm py-0 px-2 small"
                                        @click="openTracker(b)"
                                    >
                                        <i class="bi bi-broadcast me-1"></i>{{ b.tracking_label || b.trek_status }}
                                    </button>
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
                                        <i class="bi bi-trophy-fill text-warning me-1"></i>Finished
                                    </span>
                                </td>
                                <td>
                                    <span class="fw-semibold">{{ b.staff_name || 'Unassigned' }}</span>
                                </td>
                            </tr>
                            <tr v-if="bookings.length === 0">
                                <td colspan="10" class="text-center text-muted py-4">
                                    <i class="bi bi-journal-x fs-3 d-block mb-2"></i>
                                    No bookings found in this category. Explore our open treks in <router-link to="/user/browse">Browse Treks</router-link>!
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

        <!-- Milestone 6: Live Trek Status Tracking Modal -->
        <div v-if="showTrackModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">
                            <i class="bi bi-geo-alt-fill text-danger me-2"></i>Expedition Status Tracker
                        </h5>
                        <button type="button" class="btn-close" @click="showTrackModal = false"></button>
                    </div>
                    <div class="modal-body" v-if="trackingBooking">
                        <!-- Trek Overview Header -->
                        <div class="p-3 bg-light rounded mb-4">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h5 class="fw-bold mb-1">{{ trackingBooking.trek_name }}</h5>
                                    <span class="text-muted small">
                                        <i class="bi bi-geo-alt me-1"></i>{{ trackingBooking.trek_location }} ·
                                        <i class="bi bi-calendar-event ms-2 me-1"></i>{{ trackingBooking.trek_start_date }} to {{ trackingBooking.trek_end_date }}
                                    </span>
                                </div>
                                <span class="badge bg-primary fs-6">{{ trackingBooking.tracking_label }}</span>
                            </div>
                        </div>

                        <!-- 4-Step Visual Progress Stepper -->
                        <h6 class="fw-bold mb-3">Trek Progress Timeline</h6>
                        <div class="d-flex justify-content-between position-relative mb-4 text-center">
                            <!-- Step 1: Confirmed -->
                            <div class="flex-grow-1">
                                <div
                                    class="rounded-circle mx-auto d-flex align-items-center justify-content-center text-white mb-2"
                                    :class="trackingBooking.tracking_stage >= 1 ? 'bg-success' : 'bg-secondary'"
                                    style="width: 42px; height: 42px;"
                                >
                                    <i class="bi bi-check-circle"></i>
                                </div>
                                <div class="small fw-semibold">1. Confirmed</div>
                                <div class="text-muted" style="font-size: 0.75rem;">Slot Reserved</div>
                            </div>

                            <!-- Step 2: Started -->
                            <div class="flex-grow-1">
                                <div
                                    class="rounded-circle mx-auto d-flex align-items-center justify-content-center text-white mb-2"
                                    :class="trackingBooking.tracking_stage >= 2 ? 'bg-success' : 'bg-secondary'"
                                    style="width: 42px; height: 42px;"
                                >
                                    <i class="bi bi-flag"></i>
                                </div>
                                <div class="small fw-semibold">2. Started</div>
                                <div class="text-muted" style="font-size: 0.75rem;">Basecamp Briefing</div>
                            </div>

                            <!-- Step 3: Ongoing -->
                            <div class="flex-grow-1">
                                <div
                                    class="rounded-circle mx-auto d-flex align-items-center justify-content-center text-white mb-2"
                                    :class="trackingBooking.tracking_stage >= 3 ? 'bg-warning text-dark' : 'bg-secondary'"
                                    style="width: 42px; height: 42px;"
                                >
                                    <i class="bi bi-compass"></i>
                                </div>
                                <div class="small fw-semibold">3. Ongoing</div>
                                <div class="text-muted" style="font-size: 0.75rem;">On the Trail</div>
                            </div>

                            <!-- Step 4: Completed -->
                            <div class="flex-grow-1">
                                <div
                                    class="rounded-circle mx-auto d-flex align-items-center justify-content-center text-white mb-2"
                                    :class="trackingBooking.tracking_stage >= 4 ? 'bg-success' : 'bg-secondary'"
                                    style="width: 42px; height: 42px;"
                                >
                                    <i class="bi bi-trophy"></i>
                                </div>
                                <div class="small fw-semibold">4. Completed</div>
                                <div class="text-muted" style="font-size: 0.75rem;">Summit Achieved</div>
                            </div>
                        </div>

                        <!-- Guide and Itinerary Information -->
                        <div class="border rounded p-3">
                            <h6 class="fw-bold mb-2">Assigned Trek Guide</h6>
                            <div class="row g-2 small">
                                <div class="col-md-6">
                                    <strong>Guide Name:</strong> {{ trackingBooking.staff_name || 'Unassigned' }}
                                </div>
                                <div class="col-md-6" v-if="trackingBooking.staff_phone">
                                    <strong>Contact:</strong> {{ trackingBooking.staff_phone }}
                                </div>
                                <div class="col-md-6" v-if="trackingBooking.staff_email">
                                    <strong>Email:</strong> {{ trackingBooking.staff_email }}
                                </div>
                                <div class="col-md-6">
                                    <strong>Total Duration:</strong> {{ trackingBooking.trek_duration || 'N/A' }} Days
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" @click="showTrackModal = false">Close</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Enhancement 2: Mock Payment Simulation Modal -->
        <div v-if="showPayModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title fw-bold">
                            <i class="bi bi-shield-lock-fill me-2"></i>Secure Payment Gateway (Mock)
                        </h5>
                        <button type="button" class="btn-close btn-close-white" @click="showPayModal = false"></button>
                    </div>
                    <div class="modal-body" v-if="payingBooking">
                        <div class="p-3 bg-light rounded mb-3 text-center">
                            <span class="text-muted small d-block">Amount Due</span>
                            <h2 class="fw-bold text-success mb-1">₹{{ payingBooking.trek_price }}</h2>
                            <span class="fw-semibold">{{ payingBooking.trek_name }}</span>
                        </div>

                        <label class="form-label fw-bold">Select Payment Method</label>
                        <div class="d-flex flex-column gap-2 mb-3">
                            <label class="form-check border p-2 rounded d-flex align-items-center cursor-pointer" :class="{ 'border-success bg-light': selectedPayMethod === 'UPI' }">
                                <input class="form-check-input me-2" type="radio" value="UPI" v-model="selectedPayMethod">
                                <i class="bi bi-phone me-2 text-primary"></i>
                                <div>
                                    <div class="fw-semibold">UPI / QR Code</div>
                                    <small class="text-muted">GPay, PhonePe, Paytm</small>
                                </div>
                            </label>
                            <label class="form-check border p-2 rounded d-flex align-items-center cursor-pointer" :class="{ 'border-success bg-light': selectedPayMethod === 'Card' }">
                                <input class="form-check-input me-2" type="radio" value="Card" v-model="selectedPayMethod">
                                <i class="bi bi-credit-card me-2 text-danger"></i>
                                <div>
                                    <div class="fw-semibold">Credit / Debit Card</div>
                                    <small class="text-muted">Visa, MasterCard, RuPay</small>
                                </div>
                            </label>
                            <label class="form-check border p-2 rounded d-flex align-items-center cursor-pointer" :class="{ 'border-success bg-light': selectedPayMethod === 'NetBanking' }">
                                <input class="form-check-input me-2" type="radio" value="NetBanking" v-model="selectedPayMethod">
                                <i class="bi bi-bank me-2 text-success"></i>
                                <div>
                                    <div class="fw-semibold">Net Banking</div>
                                    <small class="text-muted">All major Indian banks</small>
                                </div>
                            </label>
                        </div>
                        <div class="alert alert-info py-2 px-3 small mb-0">
                            <i class="bi bi-info-circle me-1"></i>This is a simulated sandbox payment flow for academic evaluation (Enhancement 2). No actual charges will occur.
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" @click="showPayModal = false" :disabled="paymentProcessing">Cancel</button>
                        <button type="button" class="btn btn-success fw-semibold" @click="processPaymentSimulation" :disabled="paymentProcessing">
                            <span v-if="paymentProcessing" class="spinner-border spinner-border-sm me-1"></span>
                            <span v-else><i class="bi bi-lock-fill me-1"></i></span>
                            Pay ₹{{ payingBooking ? payingBooking.trek_price : 0 }} Now
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
