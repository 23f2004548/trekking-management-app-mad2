<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import StatsCard from "../../components/StatsCard.vue"
import { Chart, registerables } from "chart.js"

Chart.register(...registerables)

const router = useRouter()
const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const userName = ref(localStorage.getItem("user_name") || "Trekker")
const stats = ref({
    total_bookings: 0,
    confirmed_bookings: 0,
    pending_bookings: 0,
    diff_labels: ["Easy", "Moderate", "Hard"],
    diff_counts: [0, 0, 0]
})
const loading = ref(true)
const chartCanvas = ref(null)
let chartInstance = null

async function fetchDashboard() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/user/dashboard`, {
            headers: { Authorization: "Bearer " + token }
        })
        stats.value = res.data.stats
        if (res.data.user_name) {
            userName.value = res.data.user_name
        }

        await nextTick()
        renderChart(stats.value.diff_labels, stats.value.diff_counts)
    } catch (err) {
        console.error("Failed to load user dashboard:", err)
    } finally {
        loading.value = false
    }
}

function renderChart(labels, counts) {
    if (!chartCanvas.value) return
    if (chartInstance) {
        chartInstance.destroy()
    }
    chartInstance = new Chart(chartCanvas.value, {
        type: "doughnut",
        data: {
            labels: labels && labels.length ? labels : ["Easy", "Moderate", "Hard"],
            datasets: [{
                data: counts && counts.some(c => c > 0) ? counts : [0, 0, 0],
                backgroundColor: ["#198754", "#ffc107", "#dc3545"],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    })
}

onMounted(() => {
    fetchDashboard()
})

onBeforeUnmount(() => {
    if (chartInstance) {
        chartInstance.destroy()
    }
})
</script>

<template>
    <div>
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="fw-bold mb-0">Welcome, {{ userName }}!</h4>
            <button class="btn btn-primary btn-sm" @click="router.push('/user/browse')">
                <i class="bi bi-compass me-1"></i>Browse Treks
            </button>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else>
            <!-- Stat Cards matching MAD 1 user_dashboard.html -->
            <div class="row g-3 mb-4">
                <div class="col-4">
                    <StatsCard
                        card_title="Total Bookings"
                        :card_value="stats.total_bookings"
                        icon="bi-bookmark-check"
                    />
                </div>
                <div class="col-4">
                    <StatsCard
                        card_title="Confirmed Treks"
                        :card_value="stats.confirmed_bookings"
                        icon="bi-check-circle"
                    />
                </div>
                <div class="col-4">
                    <StatsCard
                        card_title="Pending Bookings"
                        :card_value="stats.pending_bookings"
                        icon="bi-hourglass-split"
                    />
                </div>
            </div>

            <!-- Bookings by Difficulty Chart matching MAD 1 user_dashboard.html -->
            <div class="row g-3 mb-4">
                <div class="col-12">
                    <div class="card shadow-sm border-0 bg-white">
                        <div class="card-body p-4">
                            <h5 class="fw-bold mb-3 text-center">Bookings by Difficulty</h5>
                            <div style="height: 250px; position: relative;">
                                <canvas ref="chartCanvas"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
