<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import axios from "axios"

const route = useRoute()
const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const treks = ref([])
const selectedTrekId = ref("")
const selectedTrek = ref(null)
const participants = ref([])
const loading = ref(true)
const error = ref("")
const success = ref("")

async function fetchAssignedTreks() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/staff/treks`, {
            headers: { Authorization: "Bearer " + token }
        })
        treks.value = res.data

        // Auto-select trek from route query or default to first trek
        if (route.query.trek_id) {
            selectedTrekId.value = parseInt(route.query.trek_id)
        } else if (treks.value.length > 0) {
            selectedTrekId.value = treks.value[0].id
        }

        if (selectedTrekId.value) {
            await fetchParticipants()
        }
    } catch (err) {
        error.value = "Failed to load assigned treks"
    } finally {
        loading.value = false
    }
}

async function fetchParticipants() {
    if (!selectedTrekId.value) return
    try {
        const res = await axios.get(`${BASE_URL}/staff/treks/${selectedTrekId.value}/participants`, {
            headers: { Authorization: "Bearer " + token }
        })
        selectedTrek.value = res.data.trek
        participants.value = res.data.participants
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to load participants"
    }
}

async function updateParticipantStatus(bookingId, status) {
    error.value = ""
    success.value = ""
    try {
        await axios.post(`${BASE_URL}/staff/treks/${selectedTrekId.value}/participants/${bookingId}/status`, { status }, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = `Participant status updated to ${status}`
        fetchParticipants()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to update participant"
    }
}

function getBadge(status) {
    if (status === "Booked") return "bg-primary"
    if (status === "Completed") return "bg-success"
    if (status === "Cancelled") return "bg-danger"
    return "bg-secondary"
}

onMounted(() => {
    fetchAssignedTreks()
})
</script>

<template>
    <div class="container py-4">
        <h2 class="fw-bold mb-1">Participant Management</h2>
        <p class="text-muted small mb-4">View and manage registered trekkers for your expeditions</p>

        <div v-if="success" class="alert alert-success py-2 small alert-dismissible">
            {{ success }}
            <button type="button" class="btn-close btn-sm" @click="success = ''"></button>
        </div>
        <div v-if="error" class="alert alert-danger py-2 small alert-dismissible">
            {{ error }}
            <button type="button" class="btn-close btn-sm" @click="error = ''"></button>
        </div>

        <!-- Trek Selector -->
        <div class="card p-3 shadow-sm border-0 mb-4">
            <div class="row align-items-center">
                <div class="col-md-3">
                    <label class="form-label fw-semibold mb-md-0">Select Expedition:</label>
                </div>
                <div class="col-md-6">
                    <select v-model="selectedTrekId" class="form-select" @change="fetchParticipants">
                        <option v-for="t in treks" :key="t.id" :value="t.id">
                            {{ t.name }} ({{ t.location }} - Status: {{ t.status }})
                        </option>
                    </select>
                </div>
                <div class="col-md-3 text-md-end mt-2 mt-md-0" v-if="selectedTrek">
                    <span class="badge bg-secondary fs-6">{{ participants.length }} Registered</span>
                </div>
            </div>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <!-- Participants Table -->
        <div v-else class="card shadow-sm border-0">
            <div class="card-header bg-white py-3" v-if="selectedTrek">
                <h5 class="fw-bold mb-0">Roster for: {{ selectedTrek.name }}</h5>
                <span class="text-muted small">Dates: {{ selectedTrek.start_date }} → {{ selectedTrek.end_date }}</span>
            </div>

            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>#</th>
                            <th>Trekker Name</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Booking Date</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="p in participants" :key="p.booking_id">
                            <td>{{ p.booking_id }}</td>
                            <td class="fw-semibold">{{ p.user_name }}</td>
                            <td>{{ p.user_username }}</td>
                            <td>{{ p.user_email }}</td>
                            <td class="small">{{ p.booking_date }}</td>
                            <td>
                                <span class="badge" :class="getBadge(p.status)">{{ p.status }}</span>
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button
                                        v-if="p.status !== 'Completed'"
                                        class="btn btn-outline-success"
                                        @click="updateParticipantStatus(p.booking_id, 'Completed')"
                                    >
                                        Mark Completed
                                    </button>
                                    <button
                                        v-if="p.status !== 'Cancelled'"
                                        class="btn btn-outline-danger"
                                        @click="updateParticipantStatus(p.booking_id, 'Cancelled')"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        v-if="p.status === 'Cancelled'"
                                        class="btn btn-outline-primary"
                                        @click="updateParticipantStatus(p.booking_id, 'Booked')"
                                    >
                                        Re-admit
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr v-if="participants.length === 0">
                            <td colspan="7" class="text-center text-muted py-4">No participants registered for this trek yet</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
