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

const systemOverviewCanvas = ref(null)
const bookingStatusCanvas = ref(null)
const difficultyCanvas = ref(null)
let systemOverviewChart = null
let bookingStatusChart = null
let difficultyChart = null

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

        loading.value = false
        await nextTick()
        renderCharts()
    } catch (err) {
        console.error("Failed to load reports:", err)
        loading.value = false
    }
}

function renderCharts() {
    if (!report.value) return

    if (systemOverviewCanvas.value) {
        if (systemOverviewChart) systemOverviewChart.destroy()
        systemOverviewChart = new Chart(systemOverviewCanvas.value, {
            type: "bar",
            data: {
                labels: ["Total Treks", "Total Bookings", "Active Users"],
                datasets: [{
                    data: [
                        report.value.total_treks || 0,
                        report.value.total_bookings || 0,
                        report.value.active_users || 0
                    ],
                    backgroundColor: ["#0d6efd", "#198754", "#0dcaf0"],
                    borderRadius: 0,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, precision: 0 },
                        grid: { color: "#e9ecef" }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        })
    }

    if (bookingStatusCanvas.value) {
        if (bookingStatusChart) bookingStatusChart.destroy()
        bookingStatusChart = new Chart(bookingStatusCanvas.value, {
            type: "doughnut",
            data: {
                labels: ["Confirmed", "Pending", "Cancelled"],
                datasets: [{
                    data: [
                        report.value.booking_stats?.confirmed ?? report.value.booking_stats?.booked ?? 0,
                        report.value.booking_stats?.pending || 0,
                        report.value.booking_stats?.cancelled || 0
                    ],
                    backgroundColor: ["#198754", "#ffc107", "#dc3545"],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "60%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            boxWidth: 24,
                            padding: 16,
                            font: { size: 12 }
                        }
                    }
                }
            }
        })
    }

    if (difficultyCanvas.value) {
        if (difficultyChart) difficultyChart.destroy()
        difficultyChart = new Chart(difficultyCanvas.value, {
            type: "bar",
            data: {
                labels: ["Easy", "Moderate", "Hard"],
                datasets: [{
                    data: [
                        report.value.difficulty_distribution?.Easy || 0,
                        report.value.difficulty_distribution?.Moderate || 0,
                        report.value.difficulty_distribution?.Hard || 0
                    ],
                    backgroundColor: ["#198754", "#ffc107", "#dc3545"],
                    borderRadius: 0,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, precision: 0 },
                        grid: { color: "#e9ecef" }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
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
    if (systemOverviewChart) systemOverviewChart.destroy()
    if (bookingStatusChart) bookingStatusChart.destroy()
    if (difficultyChart) difficultyChart.destroy()
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

            <div class="row g-3 mb-4">
                <div class="col-md-6">
                    <div class="card p-4 shadow-sm border-0 h-100 bg-white">
                        <h5 class="fw-bold mb-3 text-center">System Overview</h5>
                        <div style="height: 270px; position: relative;">
                            <canvas ref="systemOverviewCanvas"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card p-4 shadow-sm border-0 h-100 bg-white">
                        <h5 class="fw-bold mb-3 text-center">Booking Status Distribution</h5>
                        <div style="height: 270px; position: relative;">
                            <canvas ref="bookingStatusCanvas"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row g-3 mb-4">
                <div class="col-md-6">
                    <div class="card p-4 shadow-sm border-0 h-100 bg-white">
                        <h5 class="fw-bold mb-3 text-center">Treks by Difficulty Level</h5>
                        <div style="height: 270px; position: relative;">
                            <canvas ref="difficultyCanvas"></canvas>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card p-3 shadow-sm border-0 h-100 bg-white">
                        <h5 class="fw-bold mb-3">Participation Rates & Summary</h5>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <span><i class="bi bi-bookmark-check text-success me-2"></i>Confirmed Bookings</span>
                                <span class="badge bg-success rounded-pill">{{ report.booking_stats?.confirmed ?? report.booking_stats?.booked ?? 0 }}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <span><i class="bi bi-clock-history text-warning me-2"></i>Pending Bookings</span>
                                <span class="badge bg-warning text-dark rounded-pill">{{ report.booking_stats?.pending || 0 }}</span>
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
