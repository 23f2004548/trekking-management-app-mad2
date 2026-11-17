<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const treks = ref([])
const loading = ref(true)
const searchName = ref("")
const searchLocation = ref("")
const selectedDifficulty = ref("all")
const error = ref("")
const success = ref("")
const bookingTrek = ref(null)
const showConfirmModal = ref(false)

async function fetchTreks() {
    loading.value = true
    error.value = ""
    try {
        const params = new URLSearchParams()
        if (searchName.value.trim()) params.append("search", searchName.value.trim())
        if (searchLocation.value.trim()) params.append("location", searchLocation.value.trim())
        if (selectedDifficulty.value !== "all") params.append("difficulty", selectedDifficulty.value)

        const res = await axios.get(`${BASE_URL}/user/treks?${params.toString()}`, {
            headers: { Authorization: "Bearer " + token }
        })
        treks.value = res.data.treks || []
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to load treks"
    } finally {
        loading.value = false
    }
}

function resetFilters() {
    searchName.value = ""
    searchLocation.value = ""
    selectedDifficulty.value = "all"
    fetchTreks()
}

function promptBookTrek(trek) {
    bookingTrek.value = trek
    showConfirmModal.value = true
}

async function confirmBooking() {
    if (!bookingTrek.value) return
    error.value = ""
    success.value = ""
    try {
        const res = await axios.post(`${BASE_URL}/user/book/${bookingTrek.value.id}`, {}, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = res.data.message || "Trek booked successfully!"
        showConfirmModal.value = false
        bookingTrek.value = null
        fetchTreks()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to book trek"
        showConfirmModal.value = false
    }
}

onMounted(() => {
    fetchTreks()
})
</script>

<template>
    <div>
        <h4 class="fw-bold mb-3">
            <i class="bi bi-search text-primary me-2"></i>Browse Treks
        </h4>

        <!-- Alert messages -->
        <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="bi bi-check-circle-fill me-2"></i>{{ success }}
            <button type="button" class="btn-close" @click="success = ''"></button>
        </div>
        <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ error }}
            <button type="button" class="btn-close" @click="error = ''"></button>
        </div>

        <!-- Filter Card matching MAD 1 user_browse.html -->
        <div class="card shadow-sm border-0 mb-4 bg-white">
            <div class="card-body p-3">
                <form class="row g-3" @submit.prevent="fetchTreks">
                    <div class="col-md-3">
                        <input
                            type="text"
                            v-model="searchName"
                            class="form-control"
                            placeholder="Search by name..."
                        />
                    </div>
                    <div class="col-md-3">
                        <input
                            type="text"
                            v-model="searchLocation"
                            class="form-control"
                            placeholder="Search by location..."
                        />
                    </div>
                    <div class="col-md-3">
                        <select v-model="selectedDifficulty" class="form-select" @change="fetchTreks">
                            <option value="all">Difficulty: All</option>
                            <option value="easy">Easy</option>
                            <option value="moderate">Moderate</option>
                            <option value="hard">Hard</option>
                        </select>
                    </div>
                    <div class="col-md-3 d-flex gap-2">
                        <button type="submit" class="btn btn-primary flex-grow-1">
                            <i class="bi bi-funnel-fill me-1"></i>Search
                        </button>
                        <button type="button" class="btn btn-outline-secondary" @click="resetFilters">
                            Reset
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <!-- Treks Grid matching MAD 1 user_browse.html -->
        <div v-else-if="treks.length > 0" class="row row-cols-1 row-cols-md-3 g-4">
            <div v-for="trek in treks" :key="trek.id" class="col">
                <div class="card h-100 shadow-sm border-0 bg-white">
                    <img src="/trek2.jpg" class="card-img-top" alt="Trek photo" style="height: 180px; object-fit: cover;" />
                    <div class="card-body d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title fw-bold mb-0 text-dark">{{ trek.name }}</h5>
                            <span v-if="trek.difficulty?.toLowerCase() === 'easy'" class="badge bg-success">Easy</span>
                            <span v-else-if="trek.difficulty?.toLowerCase() === 'moderate'" class="badge bg-warning text-dark">Moderate</span>
                            <span v-else class="badge bg-danger">Hard</span>
                        </div>

                        <p class="card-text text-muted small mb-1">
                            <i class="bi bi-geo-alt-fill text-danger me-1"></i>{{ trek.location }}
                        </p>
                        <p class="card-text text-muted small mb-1">
                            <i class="bi bi-clock-fill text-primary me-1"></i>{{ trek.duration }} Days
                        </p>
                        <p class="card-text text-muted small mb-1">
                            <i class="bi bi-calendar-event me-1"></i>{{ trek.start_date }} to {{ trek.end_date }}
                        </p>
                        <p class="card-text text-muted small mb-1">
                            <i class="bi bi-person-badge text-secondary me-1"></i>Guide: {{ trek.staff_name }}
                        </p>
                        <p class="card-text text-muted small mb-2">
                            <i class="bi bi-tag-fill text-success me-1"></i>₹{{ trek.price }}
                        </p>
                        <p class="card-text text-muted small mb-3 flex-grow-1">
                            {{ trek.description ? trek.description.slice(0, 100) + (trek.description.length > 100 ? '...' : '') : 'No description available.' }}
                        </p>

                        <div class="mt-auto">
                            <div class="d-flex justify-content-between align-items-center mb-3 small text-muted">
                                <span>Slots Available</span>
                                <span
                                    class="fw-semibold"
                                    :class="trek.available_slots <= 3 ? 'text-danger' : 'text-success'"
                                >
                                    {{ trek.available_slots }} / {{ trek.total_slots || 20 }}
                                </span>
                            </div>

                            <button
                                v-if="trek.available_slots <= 0"
                                class="btn btn-secondary w-100"
                                disabled
                            >
                                Sold Out
                            </button>
                            <button
                                v-else-if="trek.is_booked_by_user"
                                class="btn btn-outline-success w-100"
                                disabled
                            >
                                <i class="bi bi-check-circle me-1"></i>Already Booked
                            </button>
                            <button
                                v-else
                                class="btn btn-primary w-100"
                                @click="promptBookTrek(trek)"
                            >
                                Book Now
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-else class="text-center py-5">
            <p class="text-muted">No treks found matching your criteria.</p>
        </div>

        <!-- Booking Confirmation Modal -->
        <div v-if="showConfirmModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">Confirm Trek Booking</h5>
                        <button type="button" class="btn-close" @click="showConfirmModal = false"></button>
                    </div>
                    <div class="modal-body" v-if="bookingTrek">
                        <p>Are you ready to book your spot for <strong>{{ bookingTrek.name }}</strong>?</p>
                        <ul class="list-unstyled small text-muted mb-0">
                            <li><i class="bi bi-geo-alt me-1"></i>Location: {{ bookingTrek.location }}</li>
                            <li><i class="bi bi-calendar me-1"></i>Dates: {{ bookingTrek.start_date }} to {{ bookingTrek.end_date }}</li>
                            <li><i class="bi bi-tag me-1"></i>Price: ₹{{ bookingTrek.price }}</li>
                            <li><i class="bi bi-people me-1"></i>Available Slots: {{ bookingTrek.available_slots }}</li>
                        </ul>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" @click="showConfirmModal = false">Cancel</button>
                        <button type="button" class="btn btn-primary" @click="confirmBooking">Confirm & Book</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
