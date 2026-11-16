<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import StatsCard from "../../components/StatsCard.vue"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const report = ref(null)
const loading = ref(true)

async function fetchReports() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/admin/reports`, {
            headers: { Authorization: "Bearer " + token }
        })
        report.value = res.data
    } catch (err) {
        console.error("Failed to load reports:", err)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchReports()
})
</script>

<template>
    <div class="container py-4">
        <h2 class="fw-bold mb-1">Trekking Statistics & Reports</h2>
        <p class="text-muted small mb-4">Comprehensive metrics on treks, bookings, and route popularity</p>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else-if="report">
            <!-- Key Metrics -->
            <div class="row g-3 mb-4">
                <div class="col-md-3">
                    <StatsCard card_title="Total Routes" :card_value="report.total_treks || 0" />
                </div>
                <div class="col-md-3">
                    <StatsCard card_title="Total Bookings" :card_value="report.total_bookings || 0" />
                </div>
                <div class="col-md-3">
                    <StatsCard card_title="Active Trekkers" :card_value="report.active_users || 0" />
                </div>
                <div class="col-md-3">
                    <StatsCard card_title="Completed Expeditions" :card_value="report.completed_treks || 0" />
                </div>
            </div>

            <!-- Distribution Breakdown -->
            <div class="row g-3 mb-4">
                <div class="col-md-6">
                    <div class="card p-3 shadow-sm border-0 h-100">
                        <h5 class="fw-bold mb-3">Booking Status Breakdown</h5>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Active Bookings
                                <span class="badge bg-primary rounded-pill">{{ report.booking_stats?.booked || 0 }}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Completed Expeditions
                                <span class="badge bg-success rounded-pill">{{ report.booking_stats?.completed || 0 }}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Cancelled Bookings
                                <span class="badge bg-danger rounded-pill">{{ report.booking_stats?.cancelled || 0 }}</span>
                            </li>
                        </ul>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card p-3 shadow-sm border-0 h-100">
                        <h5 class="fw-bold mb-3">Trek Difficulty Distribution</h5>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Easy Routes
                                <span class="badge bg-success rounded-pill">{{ report.difficulty_distribution?.Easy || 0 }}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Moderate Routes
                                <span class="badge bg-warning text-dark rounded-pill">{{ report.difficulty_distribution?.Moderate || 0 }}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Hard / High Altitude Routes
                                <span class="badge bg-danger rounded-pill">{{ report.difficulty_distribution?.Hard || 0 }}</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Popular Treks Table -->
            <div class="card p-3 shadow-sm border-0">
                <h5 class="fw-bold mb-3">Most Popular Treks (Top Booked)</h5>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>#</th>
                                <th>Trek Name</th>
                                <th>Location</th>
                                <th>Difficulty</th>
                                <th>Total Bookings</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="t in report.popular_treks" :key="t.id">
                                <td>{{ t.id }}</td>
                                <td class="fw-semibold">{{ t.name }}</td>
                                <td>{{ t.location }}</td>
                                <td><span class="badge bg-secondary">{{ t.difficulty }}</span></td>
                                <td><span class="badge bg-info text-dark">{{ t.booking_count }} Bookings</span></td>
                                <td><span class="badge bg-success">{{ t.status }}</span></td>
                            </tr>
                            <tr v-if="!report.popular_treks || report.popular_treks.length === 0">
                                <td colspan="6" class="text-center text-muted py-3">No bookings data available yet</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>
