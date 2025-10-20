import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router';
import 'mapbox-gl/dist/mapbox-gl.css';
import 'ol/ol.css';
import 'floating-vue/dist/style.css'
import FloatingVue from 'floating-vue'
const app = createApp(App)
app.use(router)
app.use(FloatingVue)
app.mount('#app')
