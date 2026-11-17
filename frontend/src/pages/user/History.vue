<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import StatsCard from "../../components/StatsCard.vue"

const router = useRouter()
const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")
const userName = localStorage.getItem("user_name") || "Trekker"

const history = ref([])
const summary = ref({ total_completed: 0, total_days: 0, total_spent: 0 })
const loading = ref(true)
const error = ref("")
const searchTerm = ref("")

const selectedCert = ref(null)
const showCertModal = ref(false)

async function fetchHistory() {
    loading.value = true
    error.value = ""
    try {
        const res = await axios.get(`${BASE_URL}/user/history`, {
            headers: { Authorization: "Bearer " + token }
        })
        history.value = res.data.history || []
        if (res.data.summary) {
            summary.value = res.data.summary
        }
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to load trekking history"
    } finally {
        loading.value = false
    }
}

const filteredHistory = computed(() => {
    if (!searchTerm.value.trim()) return history.value
    const term = searchTerm.value.toLowerCase()
    return history.value.filter(item =>
        item.trek_name?.toLowerCase().includes(term) ||
        item.trek_location?.toLowerCase().includes(term) ||
        item.staff_name?.toLowerCase().includes(term)
    )
})

function viewCertificate(item) {
    selectedCert.value = item
    showCertModal.value = true
}

const exporting = ref(false)
const exportMsg = ref("")

async function exportCSV() {
    exporting.value = true
    exportMsg.value = "Initiating export..."
    error.value = ""
    try {
        const res = await axios.post(`${BASE_URL}/user/export/csv`, {}, {
            headers: { Authorization: "Bearer " + token }
        })

        if (res.data.download_url) {
            exportMsg.value = "Export ready! Downloading..."
            window.location.href = `${BASE_URL}${res.data.download_url}`
            setTimeout(() => { exporting.value = false; exportMsg.value = "" }, 2000)
        } else if (res.data.task_id) {
            exportMsg.value = "Processing in background via Celery..."
            pollExportStatus(res.data.task_id)
        }
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to export CSV"
        exporting.value = false
        exportMsg.value = ""
    }
}

async function pollExportStatus(taskId) {
    const interval = setInterval(async () => {
        try {
            const statusRes = await axios.get(`${BASE_URL}/user/export/status/${taskId}`, {
                headers: { Authorization: "Bearer " + token }
            })
            if (statusRes.data.status === "SUCCESS") {
                clearInterval(interval)
                exportMsg.value = "Export complete! Downloading..."
                window.location.href = `${BASE_URL}${statusRes.data.download_url}`
                setTimeout(() => { exporting.value = false; exportMsg.value = "" }, 2000)
            } else if (statusRes.data.status === "FAILURE") {
                clearInterval(interval)
                error.value = "Background CSV export failed"
                exporting.value = false
                exportMsg.value = ""
            }
        } catch (e) {
            clearInterval(interval)
            error.value = "Failed to poll export status"
            exporting.value = false
            exportMsg.value = ""
        }
    }, 1500)
}

onMounted(() => {
    fetchHistory()
})
</script>

<template>
    <div>
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="fw-bold mb-0">Trekking History</h4>
            <div class="d-flex gap-2">
                <button
                    class="btn btn-outline-success btn-sm"
                    @click="exportCSV"
                    :disabled="exporting"
                >
                    <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-file-earmark-spreadsheet me-1"></i>
                    {{ exporting ? exportMsg : 'Export CSV' }}
                </button>
                <button class="btn btn-primary btn-sm" @click="router.push('/user/browse')">
                    <i class="bi bi-compass me-1"></i>Find Next Trek
                </button>
            </div>
        </div>

        <div v-if="error" class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ error }}
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else>
            <!-- Milestone 6 Summary Stats Cards -->
            <div class="row g-3 mb-4">
                <div class="col-4">
                    <StatsCard
                        card_title="Completed Expeditions"
                        :card_value="summary.total_completed"
                        icon="bi-trophy-fill"
                    />
                </div>
                <div class="col-4">
                    <StatsCard
                        card_title="Days on Trail"
                        :card_value="summary.total_days + ' Days'"
                        icon="bi-clock-history"
                    />
                </div>
                <div class="col-4">
                    <StatsCard
                        card_title="Total Investment"
                        :card_value="'₹' + summary.total_spent"
                        icon="bi-tag-fill"
                    />
                </div>
            </div>

            <!-- Search input -->
            <div class="card shadow-sm border-0 mb-3 bg-white">
                <div class="card-body p-3">
                    <div class="row">
                        <div class="col-md-6">
                            <input
                                type="text"
                                v-model="searchTerm"
                                class="form-control"
                                placeholder="Search completed treks by name, location, or guide..."
                            />
                        </div>
                    </div>
                </div>
            </div>

            <!-- History Card matching MAD 1 user_trek_history.html -->
            <div class="card shadow-sm border-0 bg-white">
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-bordered table-hover table-sm align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Trek Name</th>
                                    <th>Booking Date</th>
                                    <th>Start Date</th>
                                    <th>End Date</th>
                                    <th>Location</th>
                                    <th>Difficulty</th>
                                    <th>Guide</th>
                                    <th>Status</th>
                                    <th>Certificate</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="item in filteredHistory" :key="item.id">
                                    <td class="fw-semibold">{{ item.trek_name }}</td>
                                    <td>{{ item.booking_date }}</td>
                                    <td>{{ item.trek_start_date }}</td>
                                    <td>{{ item.trek_end_date }}</td>
                                    <td><i class="bi bi-geo-alt text-danger me-1"></i>{{ item.trek_location }}</td>
                                    <td>
                                        <span v-if="item.trek_difficulty?.toLowerCase() === 'easy'" class="badge bg-success">Easy</span>
                                        <span v-else-if="item.trek_difficulty?.toLowerCase() === 'moderate'" class="badge bg-warning text-dark">Moderate</span>
                                        <span v-else class="badge bg-danger">Hard</span>
                                    </td>
                                    <td>{{ item.staff_name || 'Unassigned' }}</td>
                                    <td>
                                        <span class="badge bg-success">
                                            <i class="bi bi-trophy-fill me-1"></i>Completed
                                        </span>
                                    </td>
                                    <td>
                                        <button class="btn btn-outline-success btn-sm py-0 px-2 small" @click="viewCertificate(item)">
                                            <i class="bi bi-patch-check-fill me-1"></i>View
                                        </button>
                                    </td>
                                </tr>
                                <tr v-if="filteredHistory.length === 0">
                                    <td colspan="9" class="text-center text-muted py-4">
                                        <i class="bi bi-clock-history fs-3 d-block mb-2"></i>
                                        No completed treks found. Complete your booked expeditions to view them here!
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Completion Certificate Modal -->
        <div v-if="showCertModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-3 border-success">
                    <div class="modal-header bg-light">
                        <h5 class="modal-title fw-bold text-success">
                            <i class="bi bi-award-fill me-2"></i>Certificate of Expedition Completion
                        </h5>
                        <button type="button" class="btn-close" @click="showCertModal = false"></button>
                    </div>
                    <div class="modal-body text-center p-4" v-if="selectedCert">
                        <div class="mb-3">
                            <i class="bi bi-trophy-fill text-warning fs-1"></i>
                        </div>
                        <h4 class="fw-bold mb-1">{{ userName }}</h4>
                        <p class="text-muted small mb-3">has successfully completed the expedition</p>
                        <h5 class="fw-bold text-primary mb-2">{{ selectedCert.trek_name }}</h5>
                        <p class="text-muted small mb-1">
                            <i class="bi bi-geo-alt text-danger me-1"></i>{{ selectedCert.trek_location }} ·
                            <i class="bi bi-calendar me-1"></i>{{ selectedCert.trek_start_date }} to {{ selectedCert.trek_end_date }}
                        </p>
                        <p class="text-muted small mb-3">
                            Guide: <strong>{{ selectedCert.staff_name }}</strong> · Difficulty: <strong>{{ selectedCert.trek_difficulty }}</strong>
                        </p>
                        <div class="alert alert-success py-2 mb-0 small">
                            <i class="bi bi-check-circle-fill me-1"></i>Official TrekFlow Completion Record Verified
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" @click="showCertModal = false">Close</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
