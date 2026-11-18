<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

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
        success.value = "Trek updated successfully"
        showModal.value = false
        fetchMyTreks()
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to update trek"
    }
}

onMounted(() => {
    fetchMyTreks()
})
</script>

<template>
    <div class="container py-4">
        <h3 class="fw-bold mb-3">My Treks</h3>

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

        <div v-else class="card shadow-sm border">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light border-bottom">
                        <tr>
                            <th class="ps-3">ID</th>
                            <th>Trek Name</th>
                            <th>Location</th>
                            <th>Difficulty</th>
                            <th>Total Slots</th>
                            <th>Available Slots</th>
                            <th>Status</th>
                            <th class="text-center pe-3">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="t in treks" :key="t.id">
                            <td class="ps-3">{{ t.id }}</td>
                            <td class="fw-semibold">{{ t.name }}</td>
                            <td>{{ t.location }}</td>
                            <td>{{ t.difficulty }}</td>
                            <td>{{ t.total_slots }}</td>
                            <td>{{ t.available_slots }}</td>
                            <td>
                                <span class="badge rounded-pill px-3 py-1 text-capitalize" :class="t.status === 'upcoming' ? 'bg-primary' : (t.status === 'ongoing' ? 'bg-warning text-dark' : 'bg-success')">
                                    {{ t.status }}
                                </span>
                            </td>
                            <td class="text-center pe-3">
                                <button
                                    class="btn btn-sm btn-outline-success px-2 py-1"
                                    title="Edit Trek"
                                    @click="openEditModal(t)"
                                >
                                    <i class="bi bi-pencil-square"></i>
                                </button>
                            </td>
                        </tr>
                        <tr v-if="treks.length === 0">
                            <td colspan="8" class="text-center text-muted py-4">No treks assigned to your profile</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">Edit Trek: {{ selectedTrek?.name }}</h5>
                        <button type="button" class="btn-close" @click="showModal = false"></button>
                    </div>
                    <form @submit.prevent="saveTrekUpdate">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Available Slots (Max: {{ selectedTrek?.total_slots }})</label>
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
                                    <option value="upcoming">upcoming</option>
                                    <option value="ongoing">ongoing</option>
                                    <option value="completed">completed</option>
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
