<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"

const router = useRouter()
const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const treks = ref([])
const loading = ref(true)
const selectedTrek = ref(null)
const showModal = ref(false)
const form = ref({ available_slots: 0, status: "" })
const error = ref("")
const success = ref("")

async function fetchMyTreks() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/staff/treks`, {
            headers: { Authorization: "Bearer " + token }
        })
        treks.value = res.data
    } catch (err) {
        error.value = "Failed to load assigned treks"
    } finally {
        loading.value = false
    }
}

function openEditModal(trek) {
    selectedTrek.value = trek
    form.value = {
        available_slots: trek.available_slots,
        status: trek.status
    }
    showModal.value = true
}

async function saveTrekUpdate() {
    error.value = ""
    success.value = ""
    try {
        await axios.put(`${BASE_URL}/staff/treks/${selectedTrek.value.id}`, form.value, {
            headers: { Authorization: "Bearer " + token }
        })
        success.value = "Trek operations updated successfully"
        showModal.value = false
        fetchMyTreks()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to update trek"
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
    fetchMyTreks()
})
</script>

<template>
    <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold mb-0">My Assigned Trekking Routes</h2>
                <p class="text-muted small mb-0">Manage slots, operational statuses, and route logistics</p>
            </div>
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

        <div v-else class="card shadow-sm border-0">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>#</th>
                            <th>Trek Name</th>
                            <th>Location</th>
                            <th>Difficulty</th>
                            <th>Duration</th>
                            <th>Slots Available</th>
                            <th>Registered</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="t in treks" :key="t.id">
                            <td>{{ t.id }}</td>
                            <td class="fw-semibold">{{ t.name }}</td>
                            <td>{{ t.location }}</td>
                            <td><span class="badge bg-secondary">{{ t.difficulty }}</span></td>
                            <td>{{ t.duration }} days</td>
                            <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
                            <td>
                                <span class="badge bg-light text-dark border">{{ t.registered_trekkers }} Trekkers</span>
                            </td>
                            <td>
                                <span class="badge" :class="getBadge(t.status)">{{ t.status }}</span>
                            </td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary me-2" @click="openEditModal(t)">Edit Operations</button>
                                <button class="btn btn-sm btn-outline-secondary" @click="router.push(`/staff/participants?trek_id=${t.id}`)">Participants</button>
                            </td>
                        </tr>
                        <tr v-if="treks.length === 0">
                            <td colspan="9" class="text-center text-muted py-4">No treks assigned to your profile</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Edit Modal -->
        <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">Update Trek Status & Slots</h5>
                        <button type="button" class="btn-close" @click="showModal = false"></button>
                    </div>
                    <form @submit.prevent="saveTrekUpdate">
                        <div class="modal-body">
                            <p class="small text-muted mb-3">
                                <strong>{{ selectedTrek?.name }}</strong> (Capacity: {{ selectedTrek?.total_slots }} total)
                            </p>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Available Slots</label>
                                <input
                                    v-model="form.available_slots"
                                    type="number"
                                    min="0"
                                    :max="selectedTrek?.total_slots"
                                    class="form-control"
                                    required
                                />
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Trek Status</label>
                                <select v-model="form.status" class="form-select" required>
                                    <option value="Open">Open (Accepting Bookings)</option>
                                    <option value="Closed">Closed (Full / Suspended)</option>
                                    <option value="Started">Started (Expedition Initiated)</option>
                                    <option value="Ongoing">Ongoing (En Route)</option>
                                    <option value="Completed">Completed (Returned)</option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showModal = false">Cancel</button>
                            <button type="submit" class="btn btn-primary">Save Changes</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>
