import { createApp } from "vue";
import App from "./App.vue";
import './style.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import router from "./router";
import axios from "axios";

// Automatically attach current JWT token from localStorage on every request
axios.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = "Bearer " + token;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// Automatically handle expired/unauthorized sessions
axios.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Clear invalid/expired session
            const currentPath = window.location.pathname;
            if (currentPath !== "/login" && currentPath !== "/" && currentPath !== "/register") {
                localStorage.removeItem("token");
                localStorage.removeItem("role");
                localStorage.removeItem("user_name");
                window.location.href = "/login?expired=1";
            }
        }
        return Promise.reject(error);
    }
);

const app = createApp(App);
app.use(router);
app.mount("#app");
