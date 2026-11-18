<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const trekRoster = ref([])
const loading = ref(true)
const error = ref("")

async function fetchParticipants() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/staff/participants`, {
            headers: { Authorization: "Bearer " + token }
        })
        trekRoster.value = res.data
    } catch (err) {
        error.value = "Failed to load participants"
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchParticipants()
})
</script>

<template>
    <div class="container py-4">
        <h3 class="fw-bold mb-3">Trek Participants</h3>

        <div v-if="error" class="alert alert-danger py-2 small alert-dismissible">
            {{ error }}
            <button type="button" class="btn-close btn-sm" @click="error = ''"></button>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else>
            <div v-for="t in trekRoster" :key="t.trek_id" class="card shadow-sm border mb-4">
                <div class="card-header bg-white py-3 border-bottom">
                    <h5 class="fw-bold mb-0 text-dark">{{ t.trek_name }} - Confirmed Participants</h5>
                </div>

                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light border-bottom">
                            <tr>
                                <th class="ps-3">User Name</th>
                                <th>Email</th>
                                <th>Booking Date</th>
                                <th class="text-end pe-4">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="p in t.participants" :key="p.booking_id">
                                <td class="ps-3 fw-semibold">{{ p.user_name }}</td>
                                <td>{{ p.user_email }}</td>
                                <td class="small text-muted">{{ p.booking_date }}</td>
                                <td class="text-end pe-4">
                                    <span class="badge bg-success rounded-pill px-3 py-1">
                                        {{ p.status === 'Booked' ? 'Confirmed' : p.status }}
                                    </span>
                                </td>
                            </tr>
                            <tr v-if="t.participants.length === 0">
                                <td colspan="4" class="text-center text-muted py-3">No confirmed participants for this trek yet</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div v-if="trekRoster.length === 0" class="card shadow-sm border p-4 text-center text-muted">
                No assigned treks found for your staff profile.
            </div>
        </div>
    </div>
</template>
