<script setup>
import { ref, computed, watch } from "vue"
import { RouterView, useRoute, useRouter } from "vue-router"

const route = useRoute()
const router = useRouter()

const token = ref(localStorage.getItem("token"))
const role = ref(localStorage.getItem("role"))
const userName = ref(localStorage.getItem("user_name") || "User")

watch(route, () => {
    token.value = localStorage.getItem("token")
    role.value = localStorage.getItem("role")
    userName.value = localStorage.getItem("user_name") || "User"
})

const isAuthRoute = computed(() => {
    return route.path === "/" || route.path === "/login" || route.path === "/register"
})

const navlinks = {
    admin: [
        { label: "Dashboard", path: "/admin/dashboard", icon: "bi-house-door" },
        { label: "Treks", path: "/admin/treks", icon: "bi-suitcase" },
        { label: "Staff", path: "/admin/staff", icon: "bi-person-check" },
        { label: "Users", path: "/admin/users", icon: "bi-people" },
        { label: "Bookings", path: "/admin/bookings", icon: "bi-bookmark-fill" },
        { label: "Search", path: "/admin/search", icon: "bi-search" },
        { label: "Reports", path: "/admin/reports", icon: "bi-bar-chart-line-fill" },
    ],
    staff: [
        { label: "Dashboard", path: "/staff/dashboard", icon: "bi-house-door" },
        { label: "My Treks", path: "/staff/treks", icon: "bi-compass" },
        { label: "Participants", path: "/staff/participants", icon: "bi-people" },
        { label: "Profile", path: "/staff/profile", icon: "bi-person-circle" },
    ],
    user: [
        { label: "Dashboard", path: "/user/dashboard", icon: "bi-house-door" },
        { label: "Browse Treks", path: "/user/browse", icon: "bi-suitcase" },
        { label: "My Bookings", path: "/user/bookings", icon: "bi-bookmark-check" },
        { label: "History", path: "/user/history", icon: "bi-clock-history" },
        { label: "Profile", path: "/user/profile", icon: "bi-person-circle" },
    ]
}

const currentLinks = computed(() => {
    return navlinks[role.value] || []
})

function logout() {
    localStorage.removeItem("token")
    localStorage.removeItem("role")
    localStorage.removeItem("user_name")
    token.value = null
    role.value = null
    router.push("/login")
}
</script>

<template>
    <div v-if="isAuthRoute || !token">
        <RouterView />
    </div>

    <div v-else class="container-fluid">
        <div class="row min-vh-100 flex-nowrap">
            <aside class="col-2 sidebar d-flex flex-column border-end p-0">
                <div class="p-3 border-bottom">
                    <div class="fw-bold text-center text-md-start fs-5">TrekFlow</div>
                </div>

                <nav class="nav flex-column p-3 flex-grow-1">
                    <router-link
                        v-for="link in currentLinks"
                        :key="link.path"
                        :to="link.path"
                        class="nav-link"
                        :class="{ active: route.path.startsWith(link.path) }"
                    >
                        <span class="me-2"><i :class="'bi ' + link.icon"></i></span>
                        {{ link.label }}
                    </router-link>

                    <a href="#" class="nav-link text-danger mt-auto" @click.prevent="logout">
                        <span class="me-2"><i class="bi bi-arrow-left"></i></span>Logout
                    </a>
                </nav>
            </aside>

            <main class="col-10 p-0 d-flex flex-column">
                <nav class="navbar navbar-expand bg-white page-topbar px-4">
                    <div class="navbar-brand mb-0 fw-semibold small">Trekking Management Application</div>
                    <div class="ms-auto d-flex align-items-center gap-3">
                        <span class="small fw-semibold text-secondary">
                            <i class="bi bi-person-circle me-1"></i> {{ userName }} ({{ role }})
                        </span>
                        <button class="btn btn-sm btn-outline-danger" @click="logout">
                            <i class="bi bi-box-arrow-right me-1"></i>Logout
                        </button>
                    </div>
                </nav>

                <div class="p-4 flex-grow-1">
                    <RouterView />
                </div>
            </main>
        </div>
    </div>
</template>
