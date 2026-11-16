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
