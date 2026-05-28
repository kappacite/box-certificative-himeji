import Home from '@/views/Home.vue'
import NotFound from '@/views/NotFound.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path:'/', name:'Home', component:Home},
    {path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound}

  ],
})

export default router
