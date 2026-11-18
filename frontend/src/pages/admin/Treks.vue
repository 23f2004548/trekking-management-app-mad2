<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
function getToken() {
    return localStorage.getItem("token")
}

const treks = ref([])
const staffList = ref([])
const loading = ref(true)
const showModal = ref(false)
const isEditing = ref(false)
const editId = ref(null)
const error = ref("")
const success = ref("")

const form = ref({
    name: "",
    location: "",
    difficulty: "Moderate",
    duration: 3,
    total_slots: 15,
    available_slots: 15,
    status: "upcoming",
    start_date: "",
    end_date: "",
    staff_id: "",
    description: "",
    price: 5000
})

async function fetchTreks() {
    loading.value = true
    error.value = ""
    try {
        const curToken = getToken()
        const [trekRes, staffRes] = await Promise.all([
            axios.get(`${BASE_URL}/admin/treks`, { headers: { Authorization: "Bearer " + curToken } }),
            axios.get(`${BASE_URL}/admin/staff`, { headers: { Authorization: "Bearer " + curToken } })
        ])
        treks.value = trekRes.data || []
        staffList.value = staffRes.data || []
    } catch (err) {
        if (err.response?.status === 401) {
            error.value = "Session expired. Please log in again."
        } else {
            error.value = err.response?.data?.message || "Failed to load data"
        }
    } finally {
        loading.value = false
    }
}

function openAddModal() {
    isEditing.value = false
    editId.value = null
    form.value = {
        name: "",
        location: "",
        difficulty: "Moderate",
        duration: 3,
        total_slots: 15,
        available_slots: 15,
        status: "upcoming",
        start_date: "",
        end_date: "",
        staff_id: "",
        description: "",
        price: 5000
    }
    showModal.value = true
}

function openEditModal(trek) {
    isEditing.value = true
    editId.value = trek.id
    form.value = {
        name: trek.name,
        location: trek.location,
        difficulty: trek.difficulty,
        duration: trek.duration,
        total_slots: trek.total_slots,
        available_slots: trek.available_slots,
        status: trek.status,
        start_date: trek.start_date || "",
        end_date: trek.end_date || "",
        staff_id: trek.staff_id || "",
        description: trek.description || "",
        price: trek.price || 0
    }
    showModal.value = true
}

async function saveTrek() {
    error.value = ""
    success.value = ""
    try {
        if (isEditing.value) {
            await axios.put(`${BASE_URL}/admin/treks/${editId.value}`, form.value, {
                headers: { Authorization: "Bearer " + getToken() }
            })
            success.value = "Trek updated successfully"
        } else {
            await axios.post(`${BASE_URL}/admin/treks`, form.value, {
                headers: { Authorization: "Bearer " + getToken() }
            })
            success.value = "Trek created successfully"
        }
        showModal.value = false
        fetchTreks()
    } catch (err) {
        error.value = err.response?.data?.message || "Operation failed"
    }
}

async function deleteTrek(id) {
    if (!confirm("Are you sure you want to delete this trek route?")) return
    try {
        await axios.delete(`${BASE_URL}/admin/treks/${id}`, {
            headers: { Authorization: "Bearer " + getToken() }
        })
        fetchTreks()
    } catch (err) {
        alert("Failed to delete trek")
    }
}

onMounted(() => {
    fetchTreks()
})
</script>

<template>
    <div class="container py-4">
        <!-- Success/Error alert banner matching screenshot -->
        <div v-if="success" class="alert py-2 px-3 small border-0 mb-3" style="background-color: #d1f4ff; color: #055160;">
            {{ success }}
        </div>
        <div v-if="error" class="alert alert-danger py-2 px-3 small border-0 mb-3">
            {{ error }}
        </div>

        <div class="d-flex justify-content-between align-items-center mb-3">
            <h3 class="fw-bold mb-0">Treks</h3>
            <button class="btn btn-primary btn-sm px-3" @click="openAddModal">+ Add New Trek</button>
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
                                <span
                                    class="badge rounded-pill px-3 py-1"
                                    :class="t.status?.toLowerCase() === 'upcoming' ? 'bg-primary' : (t.status?.toLowerCase() === 'ongoing' ? 'bg-success' : 'bg-danger')"
                                >
                                    {{ t.status?.toLowerCase() === 'upcoming' ? 'Upcoming' : (t.status?.toLowerCase() === 'ongoing' ? 'Ongoing' : 'Completed') }}
                                </span>
                            </td>
                            <td class="text-center pe-3">
                                <button
                                    class="btn btn-outline-secondary btn-sm px-2 py-1 me-1"
                                    title="Edit Trek"
                                    @click="openEditModal(t)"
                                >
                                    <i class="bi bi-pencil-square text-success"></i>
                                </button>
                                <button
                                    class="btn btn-outline-secondary btn-sm px-2 py-1"
                                    title="Delete Trek"
                                    @click="deleteTrek(t.id)"
                                >
                                    <i class="bi bi-trash text-danger"></i>
                                </button>
                            </td>
                        </tr>
                        <tr v-if="treks.length === 0">
                            <td colspan="8" class="text-center text-muted py-4">No treks found</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Add/Edit Trek Modal -->
        <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold">{{ isEditing ? "Edit Trekking Route" : "Add Trekking Route" }}</h5>
                        <button type="button" class="btn-close" @click="showModal = false"></button>
                    </div>
                    <form @submit.prevent="saveTrek">
                        <div class="modal-body">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Trek Name</label>
                                    <input v-model="form.name" type="text" class="form-control" required />
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Location</label>
                                    <input v-model="form.location" type="text" class="form-control" required />
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label fw-semibold">Difficulty</label>
                                    <select v-model="form.difficulty" class="form-select">
                                        <option>Easy</option>
                                        <option>Moderate</option>
                                        <option>Hard</option>
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label fw-semibold">Duration (Days)</label>
                                    <input v-model="form.duration" type="number" min="1" class="form-control" required />
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label fw-semibold">Price (₹)</label>
                                    <input v-model="form.price" type="number" min="0" class="form-control" />
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label fw-semibold">Total Slots</label>
                                    <input v-model="form.total_slots" type="number" min="1" class="form-control" required />
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label fw-semibold">Available Slots</label>
                                    <input v-model="form.available_slots" type="number" min="0" class="form-control" required />
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label fw-semibold">Status</label>
                                    <select v-model="form.status" class="form-select">
                                        <option value="upcoming">upcoming</option>
                                        <option value="ongoing">ongoing</option>
                                        <option value="completed">completed</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">Start Date</label>
                                    <input v-model="form.start_date" type="date" class="form-control" required />
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">End Date</label>
                                    <input v-model="form.end_date" type="date" class="form-control" required />
                                </div>
                                <div class="col-md-12">
                                    <label class="form-label fw-semibold">Assign Trek Staff</label>
                                    <select v-model="form.staff_id" class="form-select">
                                        <option value="">-- Unassigned --</option>
                                        <option v-for="s in staffList" :key="s.id" :value="s.id">
                                            {{ s.name }} ({{ s.specialization || 'General Staff' }})
                                        </option>
                                    </select>
                                </div>
                                <div class="col-md-12">
                                    <label class="form-label fw-semibold">Description</label>
                                    <textarea v-model="form.description" class="form-control" rows="3"></textarea>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="showModal = false">Cancel</button>
                            <button type="submit" class="btn btn-primary">Save Trek</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>
