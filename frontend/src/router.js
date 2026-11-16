import { createRouter, createWebHistory } from "vue-router"

import LoginPage from "./pages/LoginPage.vue"
import RegisterPage from "./pages/RegisterPage.vue"
import LandingPage from "./pages/LandingPage.vue"

// Admin Pages
import AdminDashboard from "./pages/admin/Dashboard.vue"
import AdminTreks from "./pages/admin/Treks.vue"
import AdminStaff from "./pages/admin/Staff.vue"
import AdminUsers from "./pages/admin/Users.vue"
import AdminBookings from "./pages/admin/Bookings.vue"
import AdminSearch from "./pages/admin/Search.vue"
import AdminReports from "./pages/admin/Reports.vue"

// Staff Pages
import StaffDashboard from "./pages/staff/Dashboard.vue"

// User Pages
import UserDashboard from "./pages/user/Dashboard.vue"

const routes = [
    { path: "/", component: LandingPage },
    { path: "/login", component: LoginPage },
    { path: "/register", component: RegisterPage },

    // Admin Routes (protected, admin role only)
    { path: "/admin/dashboard", component: AdminDashboard, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/treks", component: AdminTreks, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/staff", component: AdminStaff, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/users", component: AdminUsers, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/bookings", component: AdminBookings, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/search", component: AdminSearch, meta: { requiresAuth: true, role: "admin" } },
    { path: "/admin/reports", component: AdminReports, meta: { requiresAuth: true, role: "admin" } },

    // Staff Routes
    { path: "/staff/dashboard", component: StaffDashboard, meta: { requiresAuth: true, role: "staff" } },

    // User Routes
    { path: "/user/dashboard", component: UserDashboard, meta: { requiresAuth: true, role: "user" } },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')

    // Allow public routes
    if (to.path === "/" || to.path === "/login" || to.path === "/register") {
        return next()
    }
    // Check authentication requirement
    if (to.meta.requiresAuth && !token) {
        return next('/login')
    }
    // Check role authorization requirement
    if (to.meta.role && to.meta.role !== role) {
        return next('/login')
    }
    next()
})

export default router
