<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <Card class="w-full max-w-md p-6">
      <CardHeader class="animate-header-loop">
        <CardTitle class="text-center text-3xl font-extrabold text-green-700">
          🌍 GIS PORTAL LOGIN
        </CardTitle>
        <CardDescription class="text-lg text-gray-600 text-center">
          Sign in to explore and manage geospatial data
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent="login">
          <div class="space-y-4">
            <div>
              <Label for="username">Username</Label>
              <Input id="username" v-model="form.username" placeholder="Enter your username" required class="mt-1" />
            </div>
            <div>
              <Label for="password">Password</Label>
              <Input id="password" type="password" v-model="form.password" placeholder="Enter your password" required
                class="mt-1" />
            </div>
          </div>
          <Button type="submit" class="w-full mt-6 bg-sky-900 hover:bg-sky-950 text-white">Login</Button>
        </form>
        <div class="flex items-center my-4">
          <div class="flex-grow border-t border-gray-300"></div>
          <span class="px-4 text-gray-500">Or</span>
          <div class="flex-grow border-t border-gray-300"></div>
        </div>
        <div class="flex flex-col justify-center md:space-y-3 md:space-x-4 w-full max-w-md mx-auto">
          <Button variant="outline"
            class="w-full flex items-center justify-center transition-colors hover:bg-[#4285f4] hover:text-white hover:border-[#4285f4]"
            @click="loginWithGoogle">
            <GoogleIcon class="w-5 h-5 mr-2 group-hover:text-white" />
            Google
          </Button>
          <Button variant="outline"
            class="w-full flex items-center justify-center transition-colors hover:bg-[#3b5998] hover:text-white hover:border-[#3b5998]"
            @click="loginWithFacebook">
            <FacebookIcon class="w-5 h-5 mr-2 group-hover:text-white" />
            Facebook
          </Button>
        </div>
      </CardContent>
      <CardFooter class="flex justify-center">
        <p class="text-sm text-gray-600">
          Don't have account? <RouterLink to="/register" class="text-blue-600 hover:underline">Register Here!
          </RouterLink>
        </p>
      </CardFooter>
    </Card>

    <!-- Overlay với Progress đè lên toàn bộ giao diện -->
    <div v-if="uploading" class="fixed inset-0 flex items-center justify-center z-50">
      <div class="absolute inset-0 bg-white"></div> <!-- Lớp phủ mờ -->
      <div class="w-3/4 max-w-lg relative flex items-center justify-center">
        <Auth_Loading></Auth_Loading>
      </div>
    </div>
  </div>
</template>

<script>
import Swal from 'sweetalert2';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import FacebookIcon from 'vue-material-design-icons/Facebook.vue'
import GoogleIcon from 'vue-material-design-icons/Google.vue'
import axios from 'axios'
import Auth_Loading from '@/components/Loading/Auth_Loading.vue';

export default {
  components: {
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
    CardFooter,
    Input,
    Button,
    Label,
    Progress,
    GoogleIcon,
    FacebookIcon,
    Auth_Loading
  },
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      uploading: false,
    }
  },
  methods: {
    async login() {
      this.uploading = true
      try {
        const response = await axios.post('http://localhost:8000/auth/user/login', this.form)
        localStorage.setItem('access_token', response.data.access_token)
        this.$router.push('/home')
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Login failed! Your username or password is incorrect.',
        });
        console.error('Đăng nhập thất bại:', error)
        this.uploading = false
      } finally {
        // Đảm bảo uploading được tắt sau khi hoàn tất
        setTimeout(() => {
          this.uploading = false
        }, 300)
      }
    },
    loginWithGoogle() {
      window.location.href = 'http://localhost:8000/auth/user/google'
    },
    loginWithFacebook() {
      window.location.href = 'http://localhost:8000/auth/user/facebook'
    }
  }
}
</script>

<style scoped>
button:hover {
  cursor: pointer;
}

.hover\:bg-\[\#4285f4\]:hover .icon {
  color: white;
}

.hover\:bg-\[\#3b5998\]:hover .icon {
  color: white;
}
@keyframes headerFadeSlide {
  0% { opacity: 0; transform: translateY(10px) scale(0.95); }
  10% { opacity: 1; transform: translateY(0) scale(1); }
  90% { opacity: 1; transform: translateY(0) scale(1); }
  100% { opacity: 0; transform: translateY(-10px) scale(0.95); }
}

.animate-header-loop {
  animation: headerFadeSlide 4s ease-in-out infinite;
}
</style>