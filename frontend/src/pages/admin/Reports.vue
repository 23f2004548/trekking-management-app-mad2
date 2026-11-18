<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue"
import axios from "axios"
import StatsCard from "../../components/StatsCard.vue"
import { Chart, registerables } from "chart.js"

Chart.register(...registerables)

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const report = ref(null)
const generatedReports = ref([])
const loading = ref(true)
const jobLoading = ref(false)
const jobMessage = ref("")
const jobError = ref("")

const bookingStatusCanvas = ref(null)
const difficultyCanvas = ref(null)
const popularBarCanvas = ref(null)
let bookingStatusChart = null
let difficultyChart = null
let popularBarChart = null

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

        await nextTick()
        renderCharts()
    } catch (err) {
        console.error("Failed to load reports:", err)
    } finally {
        loading.value = false
    }
}

function renderCharts() {
    if (!report.value) return

    // 1. Booking Status Distribution Doughnut Chart
    if (bookingStatusCanvas.value) {
        if (bookingStatusChart) bookingStatusChart.destroy()
        bookingStatusChart = new Chart(bookingStatusCanvas.value, {
            type: "doughnut",
            data: {
                labels: ["Active Bookings", "Completed Summits", "Cancelled"],
                datasets: [{
                    data: [
                        report.value.booking_stats?.booked || 0,
                        report.value.booking_stats?.completed || 0,
                        report.value.booking_stats?.cancelled || 0
                    ],
                    backgroundColor: ["#0d6efd", "#198754", "#dc3545"],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "bottom" } }
            }
        })
    }

    // 2. Trek Difficulty Distribution Pie Chart
    if (difficultyCanvas.value) {
        if (difficultyChart) difficultyChart.destroy()
        difficultyChart = new Chart(difficultyCanvas.value, {
            type: "pie",
            data: {
                labels: ["Easy", "Moderate", "Hard"],
                datasets: [{
                    data: [
                        report.value.difficulty_distribution?.Easy || 0,
                        report.value.difficulty_distribution?.Moderate || 0,
                        report.value.difficulty_distribution?.Hard || 0
                    ],
                    backgroundColor: ["#198754", "#ffc107", "#dc3545"],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "bottom" } }
            }
        })
    }

    // 3. Most Popular Treks Participation Bar Chart
    if (popularBarCanvas.value && report.value.popular_treks?.length > 0) {
        if (popularBarChart) popularBarChart.destroy()
        popularBarChart = new Chart(popularBarCanvas.value, {
            type: "bar",
            data: {
                labels: report.value.popular_treks.map(t => t.name),
                datasets: [{
                    label: "Confirmed Participants",
                    data: report.value.popular_treks.map(t => t.booking_count),
                    backgroundColor: "#0dcaf0",
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
            }
        })
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

async function clearCache() {
    jobLoading.value = true
    jobMessage.value = ""
    jobError.value = ""
    try {
        const res = await axios.post(`${BASE_URL}/admin/cache/clear`, {}, {
            headers: { Authorization: "Bearer " + token }
        })
        jobMessage.value = res.data.message || "API cache cleared successfully"
        fetchReports()
    } catch (err) {
        jobError.value = err.response?.data?.message || "Failed to clear cache"
    } finally {
        jobLoading.value = false
    }
}

onMounted(() => {
    fetchReports()
})

onBeforeUnmount(() => {
    if (bookingStatusChart) bookingStatusChart.destroy()
    if (difficultyChart) difficultyChart.destroy()
    if (popularBarChart) popularBarChart.destroy()
})
</script>

<template>
    <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold mb-0">Trekking Statistics & Reports</h2>
            </div>
            <div class="d-flex gap-2">
                <button
                    class="btn btn-outline-danger btn-sm"
                    @click="clearCache"
                    :disabled="jobLoading"
                    title="Flush Redis and in-memory API response cache"
                >
                    <i class="bi bi-arrow-clockwise me-1"></i>Purge Cache
                </button>
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

            <!-- Enhancement 2: Interactive Chart.js Visualizations -->
            <div class="row g-3 mb-4">
                <div class="col-md-6">
                    <div class="card p-4 shadow-sm border-0 h-100 bg-white">
                        <h5 class="fw-bold mb-3 text-center">
                            <i class="bi bi-pie-chart-fill text-primary me-2"></i>Participation & Booking Status
                        </h5>
                        <div style="height: 250px; position: relative;">
                            <canvas ref="bookingStatusCanvas"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card p-4 shadow-sm border-0 h-100 bg-white">
                        <h5 class="fw-bold mb-3 text-center">
                            <i class="bi bi-compass text-success me-2"></i>Route Difficulty Breakdown
                        </h5>
                        <div style="height: 250px; position: relative;">
                            <canvas ref="difficultyCanvas"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Popular Treks Chart & Table -->
            <div class="row g-3 mb-4">
                <div class="col-md-6">
                    <div class="card p-4 shadow-sm border-0 h-100 bg-white">
                        <h5 class="fw-bold mb-3 text-center">
                            <i class="bi bi-bar-chart-fill text-info me-2"></i>Participants per Popular Route
                        </h5>
                        <div style="height: 250px; position: relative;">
                            <canvas ref="popularBarCanvas"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card p-3 shadow-sm border-0 h-100 bg-white">
                        <h5 class="fw-bold mb-3">Participation Rates & Summary</h5>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <span><i class="bi bi-bookmark-check text-primary me-2"></i>Active Confirmed Bookings</span>
                                <span class="badge bg-primary rounded-pill">{{ report.booking_stats?.booked || 0 }}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <span><i class="bi bi-check2-circle text-success me-2"></i>Completed Expeditions</span>
                                <span class="badge bg-success rounded-pill">{{ report.booking_stats?.completed || 0 }}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <span><i class="bi bi-x-circle text-danger me-2"></i>Cancelled Reservations</span>
                                <span class="badge bg-danger rounded-pill">{{ report.booking_stats?.cancelled || 0 }}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <span><i class="bi bi-people text-secondary me-2"></i>Active Trekker Accounts</span>
                                <span class="badge bg-secondary rounded-pill">{{ report.active_users || 0 }}</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Milestone 7: Generated Monthly Activity Reports (HTML Archive) -->
            <div class="card p-3 shadow-sm border-0 bg-white">
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
