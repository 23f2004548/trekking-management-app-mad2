<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue"
import axios from "axios"
import StatsCard from "../../components/StatsCard.vue"
import { Chart, registerables } from "chart.js"

Chart.register(...registerables)

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const stats = ref({})
const assignedTreks = ref([])
const loading = ref(true)
const error = ref("")
const success = ref("")

const chartCanvas = ref(null)
let chartInstance = null

async function fetchDashboard() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/staff/dashboard`, {
            headers: { Authorization: "Bearer " + token }
        })
        stats.value = res.data
        assignedTreks.value = res.data.treks || []
    } catch (err) {
        error.value = "Failed to load staff dashboard"
    } finally {
        loading.value = false
    }

    await nextTick()
    renderBarChart()
}

function renderBarChart() {
    if (!chartCanvas.value || !assignedTreks.value.length) return
    if (chartInstance) chartInstance.destroy()

    chartInstance = new Chart(chartCanvas.value, {
        type: "bar",
        data: {
            labels: assignedTreks.value.map(t => t.name),
            datasets: [{
                label: "Confirmed Participants",
                data: assignedTreks.value.map(t => t.registered_trekkers || 0),
                backgroundColor: "#198754",
                borderWidth: 0,
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

onMounted(() => {
    fetchDashboard()
})

onBeforeUnmount(() => {
    if (chartInstance) chartInstance.destroy()
})
</script>

<template>
    <div class="container py-4">
        <h4 class="fw-bold mb-3">Welcome {{ stats.staff?.name || 'Staff' }}</h4>

        <div v-if="success" class="alert alert-success py-2 small alert-dismissible">
            {{ success }}
            <button type="button" class="btn-close btn-sm" @click="success = ''"></button>
        </div>
        <div v-if="error" class="alert alert-danger py-2 small alert-dismissible">
            {{ error }}
            <button type="button" class="btn-close btn-sm" @click="error = ''"></button>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else>
            <div class="row g-3 mb-4">
                <div class="col-4">
                    <StatsCard card_title="Assigned Treks" :card_value="stats.assigned_treks || 0" icon="bi-compass" />
                </div>
                <div class="col-4">
                    <StatsCard card_title="Total Participants" :card_value="stats.total_participants || 0" icon="bi-people" />
                </div>
                <div class="col-4">
                    <StatsCard card_title="Open Treks" :card_value="stats.open_treks || 0" icon="bi-map" />
                </div>
            </div>

            <div class="row mb-4" v-if="assignedTreks.length > 0">
                <div class="col-12">
                    <div class="card shadow-sm border-0 bg-white">
                        <div class="card-body p-4">
                            <h5 class="fw-bold mb-3 text-center">
                                <i class="bi bi-bar-chart-fill text-success me-2"></i>Participants per Assigned Trek
                            </h5>
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
