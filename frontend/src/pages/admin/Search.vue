<script setup>
import { ref } from "vue"
import axios from "axios"

const BASE_URL = "http://localhost:5000"
const token = localStorage.getItem("token")

const query = ref("")
const searchType = ref("all")
const results = ref(null)
const loading = ref(false)

async function executeSearch() {
    if (!query.value.trim()) return
    loading.value = true
    try {
        const res = await axios.get(`${BASE_URL}/admin/search`, {
            headers: { Authorization: "Bearer " + token },
            params: { q: query.value.trim(), type: searchType.value }
        })
        results.value = res.data
    } catch (err) {
        console.error("Search failed:", err)
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="container py-4">
        <h2 class="fw-bold mb-4">Search Database</h2>

        <!-- Search Input Bar -->
        <div class="card p-3 shadow-sm border-0 mb-4">
            <form @submit.prevent="executeSearch" class="row g-2 align-items-center">
                <div class="col-md-7">
                    <input
                        v-model="query"
                        type="text"
                        class="form-control"
                        placeholder="Search by name or ID (e.g. 'Himalayan' or '1')..."
                        required
                    />
                </div>
                <div class="col-md-3">
                    <select v-model="searchType" class="form-select">
                        <option value="all">All Categories</option>
                        <option value="trek">Treks Only</option>
                        <option value="staff">Staff Only</option>
                        <option value="user">Trekkers (Users) Only</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                        <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                        Search
                    </button>
                </div>
            </form>
        </div>

        <!-- Search Results -->
        <div v-if="results">
            <!-- Treks Results -->
            <div v-if="results.treks && results.treks.length > 0" class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-light fw-bold">Treks Found ({{ results.treks.length }})</div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Name</th>
                                <th>Location</th>
                                <th>Difficulty</th>
                                <th>Slots</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="t in results.treks" :key="t.id">
                                <td>{{ t.id }}</td>
                                <td class="fw-semibold">{{ t.name }}</td>
                                <td>{{ t.location }}</td>
                                <td>{{ t.difficulty }}</td>
                                <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
                                <td><span class="badge bg-secondary">{{ t.status }}</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Staff Results -->
            <div v-if="results.staff && results.staff.length > 0" class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-light fw-bold">Staff Members Found ({{ results.staff.length }})</div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Specialization</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="s in results.staff" :key="s.id">
                                <td>{{ s.id }}</td>
                                <td class="fw-semibold">{{ s.name }}</td>
                                <td>{{ s.email }}</td>
                                <td>{{ s.phone_number }}</td>
                                <td>{{ s.specialization || '—' }}</td>
                                <td><span class="badge" :class="s.status === 'active' ? 'bg-success' : 'bg-danger'">{{ s.status }}</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Users Results -->
            <div v-if="results.users && results.users.length > 0" class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-light fw-bold">Trekkers Found ({{ results.users.length }})</div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Name</th>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="u in results.users" :key="u.id">
                                <td>{{ u.id }}</td>
                                <td class="fw-semibold">{{ u.name }}</td>
                                <td>{{ u.username }}</td>
                                <td>{{ u.email }}</td>
                                <td><span class="badge" :class="u.is_active ? 'bg-success' : 'bg-secondary'">{{ u.is_active ? 'Active' : 'Deactivated' }}</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div v-if="results.treks.length === 0 && results.staff.length === 0 && results.users.length === 0" class="text-center text-muted py-5">
                <p class="fs-5 mb-0">No matches found for "{{ query }}"</p>
            </div>
        </div>
    </div>
</template>
