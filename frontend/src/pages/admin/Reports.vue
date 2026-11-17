<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import StatsCard from "../../components/StatsCard.vue"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const report = ref(null)
const generatedReports = ref([])
const loading = ref(true)
const jobLoading = ref(false)
const jobMessage = ref("")
const jobError = ref("")

async function fetchReports() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/admin/reports`, {
            headers: { Authorization: "Bearer " + token }
        })
        report.value = res.data

        const listRes = await axios.get(`${BASE_URL}/admin/reports/files`, {
            headers: { Authorization: "Bearer " + token }
        })
        generatedReports.value = listRes.data.reports || []
    } catch (err) {
        console.error("Failed to load reports:", err)
    } finally {
        loading.value = false
    }
}

async function triggerMonthlyReportJob() {
    jobLoading.value = true
    jobMessage.value = ""
    jobError.value = ""
    try {
        const res = await axios.post(`${BASE_URL}/admin/jobs/monthly-report`, {}, {
            headers: { Authorization: "Bearer " + token }
        })
        jobMessage.value = res.data.message || "Monthly report job triggered successfully"
        fetchReports()
    } catch (err) {
        jobError.value = err.response?.data?.message || "Failed to trigger monthly report job"
    } finally {
        jobLoading.value = false
    }
}

async function triggerDailyRemindersJob() {
    jobLoading.value = true
    jobMessage.value = ""
    jobError.value = ""
    try {
        const res = await axios.post(`${BASE_URL}/admin/jobs/daily-reminders`, {}, {
            headers: { Authorization: "Bearer " + token }
        })
        jobMessage.value = res.data.message || "Daily reminders job triggered successfully"
    } catch (err) {
        jobError.value = err.response?.data?.message || "Failed to trigger daily reminders job"
    } finally {
        jobLoading.value = false
    }
}

onMounted(() => {
    fetchReports()
})
</script>

<template>
    <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold mb-1">Trekking Statistics & Reports</h2>
                <p class="text-muted small mb-0">Comprehensive metrics on treks, bookings, and route popularity</p>
            </div>
            <div class="d-flex gap-2">
                <button
                    class="btn btn-outline-primary btn-sm"
                    @click="triggerDailyRemindersJob"
                    :disabled="jobLoading"
                >
                    <i class="bi bi-bell-fill me-1"></i>Dispatch Daily Reminders
                </button>
                <button
                    class="btn btn-primary btn-sm"
                    @click="triggerMonthlyReportJob"
                    :disabled="jobLoading"
                >
                    <i class="bi bi-file-earmark-bar-graph me-1"></i>Generate Monthly Report
                </button>
            </div>
        </div>

        <!-- Job Alerts -->
        <div v-if="jobMessage" class="alert alert-success alert-dismissible fade show py-2" role="alert">
            <i class="bi bi-check-circle-fill me-2"></i>{{ jobMessage }}
            <button type="button" class="btn-close btn-sm" @click="jobMessage = ''"></button>
        </div>
        <div v-if="jobError" class="alert alert-danger alert-dismissible fade show py-2" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ jobError }}
            <button type="button" class="btn-close btn-sm" @click="jobError = ''"></button>
        </div>

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
            <div class="card p-3 shadow-sm border-0 mb-4">
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

            <!-- Milestone 7: Generated Monthly Activity Reports (HTML Archive) -->
            <div class="card p-3 shadow-sm border-0">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="fw-bold mb-0">
                        <i class="bi bi-file-earmark-richtext text-primary me-2"></i>Automated Monthly Reports Archive
                    </h5>
                    <span class="badge bg-secondary">{{ generatedReports.length }} Reports Archived</span>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Report File</th>
                                <th>Format</th>
                                <th>Generated By</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="r in generatedReports" :key="r.filename">
                                <td class="fw-semibold">
                                    <i class="bi bi-file-earmark-text text-success me-2"></i>{{ r.filename }}
                                </td>
                                <td><span class="badge bg-info text-dark">HTML / Web Document</span></td>
                                <td>Celery Beat Scheduler</td>
                                <td>
                                    <a :href="`${BASE_URL}${r.url}`" target="_blank" class="btn btn-outline-primary btn-sm py-0 px-2">
                                        <i class="bi bi-box-arrow-up-right me-1"></i>View Report
                                    </a>
                                </td>
                            </tr>
                            <tr v-if="generatedReports.length === 0">
                                <td colspan="4" class="text-center text-muted py-3">
                                    No archived reports yet. Click "Generate Monthly Report" above to trigger a batch report.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>
