<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"

const router = useRouter()
const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const history = ref([])
const loading = ref(true)
const error = ref("")

async function fetchHistory() {
    loading.value = true
    error.value = ""
    try {
        const res = await axios.get(`${BASE_URL}/user/history`, {
            headers: { Authorization: "Bearer " + token }
        })
        history.value = res.data.history || []
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to load trekking history"
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchHistory()
})
</script>

<template>
    <div>
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="fw-bold mb-0">Trekking History</h4>
            <button class="btn btn-primary btn-sm" @click="router.push('/user/browse')">
                <i class="bi bi-compass me-1"></i>Find Next Trek
            </button>
        </div>

        <div v-if="error" class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ error }}
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <!-- History Card matching MAD 1 user_trek_history.html -->
        <div v-else class="card shadow-sm border-0 bg-white">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-bordered table-hover table-sm align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Trek Name</th>
                                <th>Booking Date</th>
                                <th>Start Date</th>
                                <th>End Date</th>
                                <th>Location</th>
                                <th>Difficulty</th>
                                <th>Guide</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in history" :key="item.id">
                                <td class="fw-semibold">{{ item.trek_name }}</td>
                                <td>{{ item.booking_date }}</td>
                                <td>{{ item.trek_start_date }}</td>
                                <td>{{ item.trek_end_date }}</td>
                                <td><i class="bi bi-geo-alt text-danger me-1"></i>{{ item.trek_location }}</td>
                                <td>
                                    <span v-if="item.trek_difficulty?.toLowerCase() === 'easy'" class="badge bg-success">Easy</span>
                                    <span v-else-if="item.trek_difficulty?.toLowerCase() === 'moderate'" class="badge bg-warning text-dark">Moderate</span>
                                    <span v-else class="badge bg-danger">Hard</span>
                                </td>
                                <td>{{ item.staff_name || 'Unassigned' }}</td>
                                <td>
                                    <span class="badge bg-success">
                                        <i class="bi bi-trophy-fill me-1"></i>Completed
                                    </span>
                                </td>
                            </tr>
                            <tr v-if="history.length === 0">
                                <td colspan="8" class="text-center text-muted py-4">
                                    <i class="bi bi-clock-history fs-3 d-block mb-2"></i>
                                    No completed treks found. Complete your booked expeditions to view them here!
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>
