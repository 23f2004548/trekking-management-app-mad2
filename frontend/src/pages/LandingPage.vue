<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import { Chart, registerables } from "chart.js"

Chart.register(...registerables)

const router = useRouter()
const BASE_URL = "http://localhost:5000"

const analytics = ref(null)
const loading = ref(true)
const diffChartCanvas = ref(null)
const popularChartCanvas = ref(null)
let diffChartInstance = null
let popularChartInstance = null

async function fetchPublicAnalytics() {
    try {
        const res = await axios.get(`${BASE_URL}/public/analytics`)
        analytics.value = res.data
        await nextTick()
        renderCharts()
    } catch (err) {
        console.error("Public analytics load error:", err)
    } finally {
        loading.value = false
    }
}

function renderCharts() {
    if (!analytics.value) return

    // Difficulty Doughnut Chart
    if (diffChartCanvas.value) {
        if (diffChartInstance) diffChartInstance.destroy()
        diffChartInstance = new Chart(diffChartCanvas.value, {
            type: "doughnut",
            data: {
                labels: analytics.value.difficulty_breakdown.labels,
                datasets: [{
                    data: analytics.value.difficulty_breakdown.counts,
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

    // Popular Treks Bar Chart
    if (popularChartCanvas.value && analytics.value.popular_treks.length > 0) {
        if (popularChartInstance) popularChartInstance.destroy()
        popularChartInstance = new Chart(popularChartCanvas.value, {
            type: "bar",
            data: {
                labels: analytics.value.popular_treks.map(p => p.name),
                datasets: [{
                    label: "Trekkers Booked",
                    data: analytics.value.popular_treks.map(p => p.bookings),
                    backgroundColor: "#0d6efd",
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

onMounted(() => {
    fetchPublicAnalytics()
})

onBeforeUnmount(() => {
    if (diffChartInstance) diffChartInstance.destroy()
    if (popularChartInstance) popularChartInstance.destroy()
})
</script>

<template>
    <div class="landing-page min-vh-100 d-flex flex-column justify-content-between py-4">
        <!-- Hero Header matching MAD 1 style -->
        <main class="container text-center mt-3 mb-4">
            <h1 class="fw-bold display-4 text-white" id="title" style="text-shadow: 0 2px 8px rgba(0,0,0,0.4);">
                TrekFlow
            </h1>
            <h4 class="fw-semibold text-white-50 mt-2">
                Conquer Trails. Leave the Chaos Behind.
            </h4>
            <div class="d-flex justify-content-center gap-3 mt-4">
                <button class="btn btn-light btn-lg px-4 shadow fw-semibold" @click="router.push('/login')">
                    <i class="bi bi-box-arrow-in-right me-1"></i>Login
                </button>
                <button class="btn btn-outline-light btn-lg px-4 shadow fw-semibold" @click="router.push('/register')">
                    <i class="bi bi-person-plus me-1"></i>Register as Trekker
                </button>
            </div>
        </main>

        <!-- Enhancement 2: Public Landing Dashboard (Read-only Analytics, No Sensitive Data) -->
        <div class="container mb-5" v-if="analytics">
            <!-- Public Metric Counter Badges -->
            <div class="row g-3 mb-4">
                <div class="col-md-4">
                    <div class="card shadow-sm border-0 text-center p-3" style="background: rgba(255,255,255,0.92); backdrop-filter: blur(4px);">
                        <div class="text-muted small fw-semibold">Open Expeditions</div>
                        <h2 class="fw-bold text-success mt-1 mb-0">{{ analytics.metrics.open_treks }}</h2>
                        <span class="small text-muted">Ready for booking</span>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card shadow-sm border-0 text-center p-3" style="background: rgba(255,255,255,0.92); backdrop-filter: blur(4px);">
                        <div class="text-muted small fw-semibold">Trekkers Served</div>
                        <h2 class="fw-bold text-primary mt-1 mb-0">{{ analytics.metrics.trekkers_served }}</h2>
                        <span class="small text-muted">Community members on trail</span>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card shadow-sm border-0 text-center p-3" style="background: rgba(255,255,255,0.92); backdrop-filter: blur(4px);">
                        <div class="text-muted small fw-semibold">Completed Summits</div>
                        <h2 class="fw-bold text-warning mt-1 mb-0">{{ analytics.metrics.completed_expeditions }}</h2>
                        <span class="small text-muted">Safe mountain journeys</span>
                    </div>
                </div>
            </div>

            <!-- Public Charts (Chart.js) -->
            <div class="row g-3 mb-4">
                <div class="col-md-6">
                    <div class="card shadow-sm border-0 p-3 h-100" style="background: rgba(255,255,255,0.95);">
                        <h6 class="fw-bold mb-3 text-center">
                            <i class="bi bi-pie-chart-fill text-success me-2"></i>Trails by Difficulty Level
                        </h6>
                        <div style="height: 220px; position: relative;">
                            <canvas ref="diffChartCanvas"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card shadow-sm border-0 p-3 h-100" style="background: rgba(255,255,255,0.95);">
                        <h6 class="fw-bold mb-3 text-center">
                            <i class="bi bi-bar-chart-line-fill text-primary me-2"></i>Most Popular Treks
                        </h6>
                        <div style="height: 220px; position: relative;">
                            <canvas ref="popularChartCanvas"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Featured Open Treks Grid -->
            <div class="card shadow-sm border-0 p-3" style="background: rgba(255,255,255,0.95);" v-if="analytics.featured_treks.length > 0">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="fw-bold mb-0">
                        <i class="bi bi-compass-fill text-danger me-2"></i>Featured Upcoming Expeditions
                    </h6>
                    <button class="btn btn-outline-dark btn-sm" @click="router.push('/login')">
                        View All in Browse
                    </button>
                </div>
                <div class="row row-cols-1 row-cols-md-3 g-3">
                    <div v-for="t in analytics.featured_treks" :key="t.id" class="col">
                        <div class="border rounded p-3 h-100 bg-white d-flex flex-column">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="fw-bold mb-0 text-dark">{{ t.name }}</h6>
                                <span v-if="t.difficulty?.toLowerCase() === 'easy'" class="badge bg-success">Easy</span>
                                <span v-else-if="t.difficulty?.toLowerCase() === 'moderate'" class="badge bg-warning text-dark">Moderate</span>
                                <span v-else class="badge bg-danger">Hard</span>
                            </div>
                            <p class="text-muted small mb-1"><i class="bi bi-geo-alt text-danger me-1"></i>{{ t.location }}</p>
                            <p class="text-muted small mb-1"><i class="bi bi-clock text-primary me-1"></i>{{ t.duration }} Days</p>
                            <div class="mt-auto d-flex justify-content-between align-items-center pt-2 border-top">
                                <span class="fw-bold text-success">₹{{ t.price }}</span>
                                <button class="btn btn-sm btn-primary py-0 px-2" @click="router.push('/login')">Book Now</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="text-center text-white mb-2">
            <i>Copyright 2026 Trekking Management App. All rights reserved.</i>
        </footer>
    </div>
</template>
