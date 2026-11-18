<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const history = ref([])
const loading = ref(true)
const error = ref("")
const exporting = ref(false)
const exportMsg = ref("")

async function fetchHistory() {
    loading.value = true
    error.value = ""
    try {
        const res = await axios.get(`${BASE_URL}/user/history`, {
            headers: { Authorization: "Bearer " + token }
        })
        history.value = res.data.history || []
    } catch (err) {
        error.value = err.response?.data?.message || "Failed to load trekking history"
    } finally {
        loading.value = false
    }
}

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
    <div class="container py-4">
        <div v-if="exportMsg" class="alert py-2 px-3 small border-0 mb-3" style="background-color: #d1f4ff; color: #055160;">
            {{ exportMsg }}
        </div>
        <div v-if="error" class="alert alert-danger py-2 px-3 small border-0 mb-3">
            {{ error }}
        </div>

        <div class="d-flex justify-content-between align-items-center mb-3">
            <h3 class="fw-bold mb-0">Trekking History</h3>
            <button
                class="btn btn-outline-success btn-sm px-3"
                @click="exportCSV"
                :disabled="exporting"
            >
                <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-file-earmark-spreadsheet me-1"></i>
                {{ exporting ? exportMsg : 'Export CSV' }}
            </button>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else class="card shadow-sm border">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light border-bottom">
                        <tr>
                            <th class="ps-3">Trek Name</th>
                            <th>Booking Date</th>
                            <th>Start Date</th>
                            <th>End Date</th>
                            <th>Location</th>
                            <th class="pe-3">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in history" :key="item.id">
                            <td class="ps-3 fw-semibold">{{ item.trek_name }}</td>
                            <td>{{ item.booking_date }}</td>
                            <td>{{ item.trek_start_date || 'N/A' }}</td>
                            <td>{{ item.trek_end_date || item.completion_date || 'N/A' }}</td>
                            <td>{{ item.trek_location || item.location }}</td>
                            <td class="pe-3">
                                <span class="badge rounded-pill bg-success px-3 py-1">
                                    Completed
                                </span>
                            </td>
                        </tr>
                        <tr v-if="history.length === 0">
                            <td colspan="6" class="text-center text-muted py-4">No completed treks found.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
