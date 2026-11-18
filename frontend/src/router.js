import { createRouter, createWebHistory } from "vue-router"

import LoginPage from "./pages/LoginPage.vue"
import RegisterPage from "./pages/RegisterPage.vue"
import LandingPage from "./pages/LandingPage.vue"

import AdminDashboard from "./pages/admin/Dashboard.vue"
import AdminTreks from "./pages/admin/Treks.vue"
import AdminStaff from "./pages/admin/Staff.vue"
import AdminUsers from "./pages/admin/Users.vue"
import AdminBookings from "./pages/admin/Bookings.vue"
import AdminSearch from "./pages/admin/Search.vue"
import AdminReports from "./pages/admin/Reports.vue"

import StaffDashboard from "./pages/staff/Dashboard.vue"
import StaffTreks from "./pages/staff/Treks.vue"
import StaffParticipants from "./pages/staff/Participants.vue"
import StaffProfile from "./pages/staff/Profile.vue"

import UserDashboard from "./pages/user/Dashboard.vue"
import UserBrowse from "./pages/user/Browse.vue"
import UserBookings from "./pages/user/Bookings.vue"
import UserHistory from "./pages/user/History.vue"
import UserProfile from "./pages/user/Profile.vue"

const routes = [
    { path: "/", component: LandingPage },
    { path: "/login", component: LoginPage },
    { path: "/register", component: RegisterPage },

    { path: "/admin/dashboard", component: AdminDashboard, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/treks", component: AdminTreks, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/staff", component: AdminStaff, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/users", component: AdminUsers, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/bookings", component: AdminBookings, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/search", component: AdminSearch, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/reports", component: AdminReports, meta: { requiresAuth: true, role: "admin" } },

    { path: "/staff/dashboard", component: StaffDashboard, meta: { requiresAuth: true, role: "staff" } },
    { path: "/staff/treks", component: StaffTreks, meta: { requiresAuth: true, role: "staff" } },
    { path: "/staff/participants", component: StaffParticipants, meta: { requiresAuth: true, role: "staff" } },
    { path: "/staff/profile", component: StaffProfile, meta: { requiresAuth: true, role: "staff" } },

    { path: "/user/dashboard", component: UserDashboard, meta: { requiresAuth: true, role: "user" } },
    { path: "/user/browse", component: UserBrowse, meta: { requiresAuth: true, role: "user" } },
    { path: "/user/bookings", component: UserBookings, meta: { requiresAuth: true, role: "user" } },
    { path: "/user/history", component: UserHistory, meta: { requiresAuth: true, role: "user" } },
    { path: "/user/profile", component: UserProfile, meta: { requiresAuth: true, role: "user" } },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')

    if (to.path === "/" || to.path === "/login" || to.path === "/register") {
        return next()
    }
    if (to.meta.requiresAuth && !token) {
        return next('/login')
    }
    if (to.meta.role && to.meta.role !== role) {
        return next('/login')
    }
    next()
})

export default router
