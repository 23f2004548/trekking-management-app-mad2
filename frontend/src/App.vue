<script setup>
import { ref, watch } from "vue"
import { RouterView, useRoute } from "vue-router"
import NavBar from "./components/NavBar.vue"

const route = useRoute()
const token = ref(localStorage.getItem("token"))

watch(route, () => {
    token.value = localStorage.getItem("token")
})
</script>

<template>
    <NavBar v-if="token" />
    <main>
        <RouterView />
    </main>
</template>
