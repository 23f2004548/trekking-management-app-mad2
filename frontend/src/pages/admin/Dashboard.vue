<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import StatsCard from "../../components/StatsCard.vue"

const router = useRouter()
const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const stats = ref({})
const recentTreks = ref([])
const loading = ref(true)

async function getDashboardData() {
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/admin/dashboard`, {
            headers: { Authorization: "Bearer " + token }
        })
        stats.value = res.data

        const trekRes = await axios.get(`${BASE_URL}/admin/treks`, {
            headers: { Authorization: "Bearer " + token }
        })
        recentTreks.value = trekRes.data.slice(0, 5)
    } catch (err) {
        console.error("Dashboard data load error:", err)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    getDashboardData()
})
</script>

<template>
    <div>
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="fw-bold mb-0">Dashboard</h4>
            <div class="d-flex gap-2">
                <button class="btn btn-primary btn-sm" @click="router.push('/admin/treks')">+ Add Trek</button>
                <button class="btn btn-outline-secondary btn-sm" @click="router.push('/admin/staff')">+ Add Staff</button>
            </div>
        </div>

        <!-- Stats Cards -->
        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
        </div>
        <div v-else>
            <div class="row g-3 mb-4">
                <div class="col-3">
                    <StatsCard card_title="Total Treks" :card_value="stats.total_treks || 0" icon="bi-suitcase" />
                </div>
                <div class="col-3">
                    <StatsCard card_title="Total Users" :card_value="stats.total_users || 0" icon="bi-people" />
                </div>
                <div class="col-3">
                    <StatsCard card_title="Total Staff" :card_value="stats.total_staff || 0" icon="bi-person-check" />
                </div>
                <div class="col-3">
                    <StatsCard card_title="Total Bookings" :card_value="stats.total_bookings || 0" icon="bi-bookmark-check" />
                </div>
                <div class="col-3">
                    <StatsCard card_title="Open Treks" :card_value="stats.open_treks || 0" icon="bi-compass" />
                </div>
                <div class="col-3">
                    <StatsCard card_title="Active Bookings" :card_value="stats.active_bookings || 0" icon="bi-calendar-check" />
                </div>
                <div class="col-3">
                    <StatsCard card_title="Blocked Users" :card_value="stats.blocked_users || 0" icon="bi-person-x" />
                </div>
                <div class="col-3">
                    <StatsCard card_title="Blacklisted Staff" :card_value="stats.blacklisted_staff || 0" icon="bi-shield-x" />
                </div>
            </div>

            <!-- Recent Treks Overview (Page Card) -->
            <div class="page-card p-3 shadow-sm mb-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div class="section-title">Recent Trekking Routes</div>
                    <router-link to="/admin/treks" class="small text-decoration-none fw-semibold">View All →</router-link>
                </div>

                <div v-if="recentTreks.length === 0" class="text-muted text-center py-3">No treks available yet</div>
                <div v-else class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Trek Name</th>
                                <th>Location</th>
                                <th>Difficulty</th>
                                <th>Slots</th>
                                <th>Assigned Staff</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="t in recentTreks" :key="t.id">
                                <td class="fw-semibold">{{ t.name }}</td>
                                <td>{{ t.location }}</td>
                                <td><span class="badge bg-secondary">{{ t.difficulty }}</span></td>
                                <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
                                <td>{{ t.staff_name }}</td>
                                <td>
                                    <span class="badge" :class="t.status === 'Open' ? 'bg-success' : 'bg-warning text-dark'">
                                        {{ t.status }}
                                    </span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>
