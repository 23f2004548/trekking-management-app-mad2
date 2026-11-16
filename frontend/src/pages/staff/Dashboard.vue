<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import StatsCard from "../../components/StatsCard.vue"

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
}

async function updateTrekStatus(trekId, status) {
    error.value = ""
    success.value = ""
    try {
        await axios.put(`${BASE_URL}/staff/treks/${trekId}`, { status }, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = `Trek status marked as ${status}`
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
        success.value = "Available slots updated successfully"
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
</script>

<template>
    <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
            <div>
                <h2 class="fw-bold mb-0">Trek Staff Operations Dashboard</h2>
                <p class="text-muted small mb-0">
                    Logged in as: <strong>{{ stats.staff?.name || 'Trek Staff' }}</strong> 
                    ({{ stats.staff?.specialization || 'Expedition Guide' }})
                </p>
            </div>
            <button class="btn btn-outline-primary btn-sm" @click="router.push('/staff/profile')">Edit My Profile</button>
        </div>

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
            <!-- Stats Cards -->
            <div class="row g-3 mb-4">
                <div class="col-md-4">
                    <StatsCard card_title="My Assigned Treks" :card_value="stats.assigned_treks || 0" />
                </div>
                <div class="col-md-4">
                    <StatsCard card_title="Open Treks" :card_value="stats.open_treks || 0" />
                </div>
                <div class="col-md-4">
                    <StatsCard card_title="Registered Trekkers" :card_value="stats.total_participants || 0" />
                </div>
            </div>

            <!-- Assigned Treks List -->
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                    <h5 class="fw-bold mb-0">My Assigned Expeditions</h5>
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
                                <th>Available / Total Slots</th>
                                <th>Registered Trekkers</th>
                                <th>Current Status</th>
                                <th>Manage Status & Slots</th>
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
                                    <span class="badge bg-info text-dark fs-6">{{ t.registered_trekkers }} Trekkers</span>
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
                                            Mark Completed
                                        </button>
                                        <button
                                            v-if="t.status === 'Open'"
                                            class="btn btn-sm btn-outline-danger"
                                            @click="updateTrekStatus(t.id, 'Closed')"
                                        >
                                            Close Slots
                                        </button>
                                        <button
                                            v-if="t.status === 'Closed'"
                                            class="btn btn-sm btn-outline-success"
                                            @click="updateTrekStatus(t.id, 'Open')"
                                        >
                                            Open Slots
                                        </button>
                                        <button
                                            class="btn btn-sm btn-outline-dark"
                                            @click="router.push(`/staff/participants?trek_id=${t.id}`)"
                                        >
                                            Participants
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            <tr v-if="assignedTreks.length === 0">
                                <td colspan="8" class="text-center text-muted py-4">No treks assigned to you currently</td>
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
                                <strong>{{ selectedTrek?.name }}</strong> (Total capacity: {{ selectedTrek?.total_slots }} slots)
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
                                <div class="form-text small">Cannot exceed total slots of {{ selectedTrek?.total_slots }}.</div>
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
