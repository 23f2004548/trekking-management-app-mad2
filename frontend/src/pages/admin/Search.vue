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
        <h2 class="fw-bold mb-4">
            <i class="bi bi-search me-2"></i>Search Dashboard
        </h2>

        <!-- Search Input Bar matching screenshot -->
        <form @submit.prevent="executeSearch" class="row g-3 mb-4">
            <div class="col-8">
                <input
                    v-model="query"
                    type="text"
                    class="form-control"
                    placeholder="Enter keyword..."
                    required
                />
            </div>
            <div class="col-3">
                <select v-model="searchType" class="form-select">
                    <option value="all">All</option>
                    <option value="trek">Trek</option>
                    <option value="user">User</option>
                    <option value="staff">Staff</option>
                </select>
            </div>
            <div class="col-1 d-grid">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                    <span v-else>Search</span>
                </button>
            </div>
        </form>

        <!-- Search Results -->
        <div v-if="results">
            <!-- Treks Results -->
            <div v-if="results.treks && results.treks.length > 0" class="card shadow-sm border mb-4">
                <div class="card-header bg-white py-3 border-bottom fw-bold">
                    Trek Results ({{ results.treks.length }})
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light border-bottom">
                            <tr>
                                <th class="ps-3">ID</th>
                                <th>Name</th>
                                <th>Location</th>
                                <th>Difficulty</th>
                                <th>Slots</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="t in results.treks" :key="t.id">
                                <td class="ps-3">{{ t.id }}</td>
                                <td class="fw-semibold">{{ t.name }}</td>
                                <td>{{ t.location }}</td>
                                <td>{{ t.difficulty }}</td>
                                <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
                                <td>
                                    <span
                                        class="badge rounded-pill px-3 py-1"
                                        :class="t.status?.toLowerCase() === 'upcoming' ? 'bg-primary' : (t.status?.toLowerCase() === 'ongoing' ? 'bg-success' : 'bg-danger')"
                                    >
                                        {{ t.status?.toLowerCase() === 'upcoming' ? 'Upcoming' : (t.status?.toLowerCase() === 'ongoing' ? 'Ongoing' : 'Completed') }}
                                    </span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Users Results -->
            <div v-if="results.users && results.users.length > 0" class="card shadow-sm border mb-4">
                <div class="card-header bg-white py-3 border-bottom fw-bold">
                    User Results ({{ results.users.length }})
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light border-bottom">
                            <tr>
                                <th class="ps-3">ID</th>
                                <th>Name</th>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="u in results.users" :key="u.id">
                                <td class="ps-3">{{ u.id }}</td>
                                <td class="fw-semibold">{{ u.name }}</td>
                                <td>{{ u.username }}</td>
                                <td>{{ u.email }}</td>
                                <td>
                                    <span
                                        class="badge rounded-pill px-3 py-1"
                                        :class="u.is_active ? 'bg-primary' : 'bg-danger'"
                                    >
                                        {{ u.is_active ? 'Active' : 'Blocked' }}
                                    </span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Staff Results -->
            <div v-if="results.staff && results.staff.length > 0" class="card shadow-sm border mb-4">
                <div class="card-header bg-white py-3 border-bottom fw-bold">
                    Staff Results ({{ results.staff.length }})
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light border-bottom">
                            <tr>
                                <th class="ps-3">ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Specialization</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="s in results.staff" :key="s.id">
                                <td class="ps-3">{{ s.id }}</td>
                                <td class="fw-semibold">{{ s.name }}</td>
                                <td>{{ s.email }}</td>
                                <td>{{ s.phone_number }}</td>
                                <td>{{ s.specialization || 'General' }}</td>
                                <td>
                                    <span
                                        class="badge rounded-pill px-3 py-1"
                                        :class="s.status?.toLowerCase() === 'approved' ? 'bg-success' : (s.status?.toLowerCase() === 'pending' ? 'bg-warning text-dark' : 'bg-danger')"
                                    >
                                        {{ s.status?.toLowerCase() === 'pending' ? 'Pending' : (s.status?.toLowerCase() === 'approved' ? 'Approved' : 'Blacklisted') }}
                                    </span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div v-if="results.treks?.length === 0 && results.staff?.length === 0 && results.users?.length === 0" class="card shadow-sm border p-4 text-center text-muted">
                No results found matching "{{ query }}"
            </div>
        </div>
    </div>
</template>
