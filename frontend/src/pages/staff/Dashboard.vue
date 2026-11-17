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

const stats = ref({})
const assignedTreks = ref([])
const loading = ref(true)
const selectedTrek = ref(null)
const showSlotModal = ref(false)
const newSlots = ref(0)
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

        await nextTick()
        renderBarChart()
    } catch (err) {
        error.value = "Failed to load staff dashboard"
    } finally {
        loading.value = false
    }
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

async function updateTrekStatus(trekId, status) {
    error.value = ""
    success.value = ""
    try {
        await axios.put(`${BASE_URL}/staff/treks/${trekId}`, { status }, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = `Trek marked as ${status}`
        fetchDashboard()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to update trek status"
    }
}

function openSlotModal(trek) {
    selectedTrek.value = trek
    newSlots.value = trek.available_slots
    showSlotModal.value = true
}

async function saveSlots() {
    error.value = ""
    success.value = ""
    try {
        await axios.put(`${BASE_URL}/staff/treks/${selectedTrek.value.id}`, { available_slots: newSlots.value }, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = "Slots updated successfully"
        showSlotModal.value = false
        fetchDashboard()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to update slots"
    }
}

function getBadge(status) {
    if (status === "Open") return "bg-success"
    if (status === "Started" || status === "Ongoing") return "bg-info text-dark"
    if (status === "Completed") return "bg-primary"
    if (status === "Closed") return "bg-danger"
    return "bg-secondary"
}

onMounted(() => {
    fetchDashboard()
})

onBeforeUnmount(() => {
    if (chartInstance) chartInstance.destroy()
})
</script>

<template>
    <div>
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
            <!-- Stats Cards in MAD 1 style -->
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

            <!-- Enhancement 2: Participants per Assigned Trek Bar Chart (MAD 1 style) -->
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

            <!-- Assigned Treks List -->
            <div class="page-card p-3 shadow-sm mb-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div class="section-title">My Assigned Expeditions</div>
                    <button class="btn btn-sm btn-outline-secondary" @click="fetchDashboard">Refresh</button>
                </div>

                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>#</th>
                                <th>Trek Name</th>
                                <th>Location</th>
                                <th>Dates</th>
                                <th>Slots</th>
                                <th>Registered</th>
                                <th>Status</th>
                                <th>Manage Operations</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="t in assignedTreks" :key="t.id">
                                <td>{{ t.id }}</td>
                                <td class="fw-semibold">{{ t.name }}</td>
                                <td>{{ t.location }}</td>
                                <td class="small">{{ t.start_date }} → {{ t.end_date }}</td>
                                <td>
                                    <span class="fw-bold">{{ t.available_slots }}</span> / {{ t.total_slots }}
                                    <button class="btn btn-link btn-sm p-0 ms-1" title="Update Slots" @click="openSlotModal(t)">✏️</button>
                                </td>
                                <td>
                                    <span class="badge bg-light text-dark border">{{ t.registered_trekkers }} Trekkers</span>
                                </td>
                                <td>
                                    <span class="badge" :class="getBadge(t.status)">{{ t.status }}</span>
                                </td>
                                <td>
                                    <div class="d-flex gap-1 flex-wrap">
                                        <button
                                            v-if="t.status !== 'Started' && t.status !== 'Completed'"
                                            class="btn btn-sm btn-outline-info"
                                            @click="updateTrekStatus(t.id, 'Started')"
                                        >
                                            Start
                                        </button>
                                        <button
                                            v-if="t.status === 'Started'"
                                            class="btn btn-sm btn-outline-primary"
                                            @click="updateTrekStatus(t.id, 'Ongoing')"
                                        >
                                            Ongoing
                                        </button>
                                        <button
                                            v-if="t.status !== 'Completed'"
                                            class="btn btn-sm btn-outline-success"
                                            @click="updateTrekStatus(t.id, 'Completed')"
                                        >
                                            Complete
                                        </button>
                                        <button
                                            v-if="t.status === 'Open'"
                                            class="btn btn-sm btn-outline-danger"
                                            @click="updateTrekStatus(t.id, 'Closed')"
                                        >
                                            Close
                                        </button>
                                        <button
                                            v-if="t.status === 'Closed'"
                                            class="btn btn-sm btn-outline-success"
                                            @click="updateTrekStatus(t.id, 'Open')"
                                        >
                                            Open
                                        </button>
                                        <button
                                            class="btn btn-sm btn-outline-secondary"
                                            @click="router.push(`/staff/participants?trek_id=${t.id}`)"
                                        >
                                            Participants
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            <tr v-if="assignedTreks.length === 0">
                                <td colspan="8" class="text-center text-muted py-4">No treks currently assigned to you</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Update Slots Modal -->
        <div v-if="showSlotModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">Update Available Slots</h5>
                        <button type="button" class="btn-close" @click="showSlotModal = false"></button>
                    </div>
                    <form @submit.prevent="saveSlots">
                        <div class="modal-body">
                            <p class="small text-muted mb-3">
                                <strong>{{ selectedTrek?.name }}</strong> (Total Capacity: {{ selectedTrek?.total_slots }})
                            </p>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Available Slots</label>
                                <input
                                    v-model="newSlots"
                                    type="number"
                                    min="0"
                                    :max="selectedTrek?.total_slots"
                                    class="form-control"
                                    required
                                />
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showSlotModal = false">Cancel</button>
                            <button type="submit" class="btn btn-primary">Save Changes</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>
