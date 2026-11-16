<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

const navlinks = {
    admin: [
        { label: "Dashboard", path: "/admin/dashboard" },
        { label: "Treks", path: "/admin/treks" },
        { label: "Staff", path: "/admin/staff" },
        { label: "Users", path: "/admin/users" },
        { label: "Bookings", path: "/admin/bookings" },
        { label: "Search", path: "/admin/search" },
        { label: "Reports", path: "/admin/reports" }
    ],
    staff: [
        { label: "Dashboard", path: "/staff/dashboard" },
        { label: "My Treks", path: "/staff/treks" },
        { label: "Participants", path: "/staff/participants" },
        { label: "Profile", path: "/staff/profile" }
    ],
    user: [
        { label: "Dashboard", path: "/user/dashboard" },
    ]
}

const links = computed(() => navlinks[localStorage.getItem("role")] || [])
const currentRole = computed(() => localStorage.getItem("role") || "")

function logout() {
    localStorage.removeItem("token")
    localStorage.removeItem("role")
    router.push("/login")
}
</script>

<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-4 shadow-sm">
        <span class="navbar-brand fw-bold" style="cursor: pointer;" @click="router.push('/')">TrekMate V2</span>
        <span class="badge bg-secondary text-uppercase ms-1">{{ currentRole }}</span>
        <div class="d-flex gap-2 ms-auto align-items-center flex-wrap">
            <button v-for="link in links" :key="link.path" class="btn btn-outline-light btn-sm" @click="router.push(link.path)">
                {{ link.label }}
            </button>
            <button class="btn btn-danger btn-sm ms-2" @click="logout">Logout</button>
        </div>
    </nav>
</template>
