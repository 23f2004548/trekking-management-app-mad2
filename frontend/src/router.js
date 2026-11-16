import { createRouter, createWebHistory } from "vue-router"

import LoginPage from "./pages/LoginPage.vue"
import RegisterPage from "./pages/RegisterPage.vue"
import LandingPage from "./pages/LandingPage.vue"

import AdminDashboard from "./pages/admin/Dashboard.vue"
import StaffDashboard from "./pages/staff/Dashboard.vue"
import UserDashboard from "./pages/user/Dashboard.vue"

const routes = [
    { path: "/", component: LandingPage },
    { path: "/login", component: LoginPage },
    { path: "/register", component: RegisterPage },

    // Role-specific protected dashboards
    { path: "/admin/dashboard", component: AdminDashboard, meta: { requiresAuth: true, role: "admin" } },
    { path: "/staff/dashboard", component: StaffDashboard, meta: { requiresAuth: true, role: "staff" } },
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
