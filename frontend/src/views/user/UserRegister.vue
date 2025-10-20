<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <Card class="w-full max-w-md p-6">
      <CardHeader class="animate-header-loop">
        <CardTitle class="text-center text-3xl font-extrabold text-green-700">
          🌍 REGISTER FOR GIS ACCESS
        </CardTitle>
        <CardDescription class="text-center text-lg text-gray-600">
          Create your account to explore and manage geospatial data
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent>
          <div class="space-y-4">
            <div>
              <Label for="username">Username</Label>
              <Input id="username" v-model="form.username" placeholder="Enter your username" required class="mt-1" />
            </div>
            <div class="relative">
              <Label for="password">Password</Label>
              <Input id="password" :type="showPassword ? 'text' : 'password'" v-model="form.password"
                placeholder="Enter your password" required class="mt-1 pr-10" @input="validatePassword" />
              <button type="button" class="absolute top-15 right-0 transform -translate-y-8 flex items-center pr-3"
                @click="togglePasswordVisibility">
                <EyeIcon v-if="!showPassword" class="w-5 h-5 text-gray-500" />
                <EyeOffIcon v-else class="w-5 h-5 text-gray-500" />
              </button>
              <p v-if="passwordError" class="text-sm text-red-500 mt-1">{{ passwordError }}</p>
            </div>
            <div class="relative">
              <Label for="retype_password">Retype Password</Label>
              <Input id="retype_password" :type="showRetypePassword ? 'text' : 'password'"
                v-model="form.retype_password" placeholder="Retype your password" required class="mt-1 pr-10"
                @input="validateRetypePassword" />
              <button type="button" class="absolute top-9 right-0 transform -translate-y-1/2 flex items-center pr-3"
                @click="toggleRetypePasswordVisibility">
                <EyeIcon v-if="!showRetypePassword" class="w-5 h-5 text-gray-500" />
                <EyeOffIcon v-else class="w-5 h-5 text-gray-500" />
              </button>
              <p v-if="retypePasswordError" class="text-sm text-red-500 mt-1">{{ retypePasswordError }}</p>
            </div>
            <div>
              <Label for="full_name">Full Name</Label>
              <Input id="full_name" v-model="form.full_name" placeholder="Enter your fullname" required class="mt-1" />
            </div>
            <div>
              <Label for="user_image">Profile Image</Label>
              <div class="mt-1">
                <input id="user_image" type="file" accept="image/*" ref="fileInput" class="hidden"
                  @change="handleImageUpload" />
                <Button variant="outline" @click="triggerFileInput" class="w-full justify-start">
                  <UploadIcon class="w-4 h-4 mr-2" />
                  Choose file
                </Button>
                <p class="text-lg text-gray-500 mt-2">{{ selectedFileName || 'No file chosen' }}</p>
              </div>
              <p v-if="imageError" class="text-sm text-red-500 mt-1">{{ imageError }}</p>
            </div>
          </div>
          <Button type="submit" @click="register" class="w-full mt-6 bg-sky-900 hover:bg-sky-950 text-white" :disabled="isFormInvalid || uploading">Register</Button>
          <Alert v-if="alertMessage" :variant="alertVariant" class="mt-4">
            <AlertDescription>{{ alertMessage }}</AlertDescription>
          </Alert>
        </form>
      </CardContent>
      <CardFooter class="flex justify-center">
        <p class="text-sm text-gray-600">
          Have an account? <RouterLink to="/login" class="text-blue-600 hover:underline">Login right now!</RouterLink>
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
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import Auth_Loading from '@/components/Loading/Auth_Loading.vue';
import { EyeIcon, EyeOffIcon, UploadIcon } from 'lucide-vue-next'
import axios from 'axios'
import Swal from 'sweetalert2';
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
    Alert,
    AlertDescription,
    EyeIcon,
    EyeOffIcon,
    UploadIcon,
    Auth_Loading
  },
  data() {
    return {
      form: {
        username: '',
        password: '',
        retype_password: '',
        full_name: '',
        user_image: null
      },
      passwordError: '',
      retypePasswordError: '',
      imageError: '',
      alertMessage: '',
      alertVariant: 'destructive',
      showPassword: false,
      showRetypePassword: false,
      uploading: false,
      uploadProgress: 0,
      selectedFileName: ''
    }
  },
  computed: {
    isFormInvalid() {
      if(!this.form.username || !this.form.password || !this.form.retype_password || !this.form.full_name || this.passwordError || this.retypePasswordError|| this.imageError) return true
      else return false
    }
  },
  methods: {
    validatePassword() {
      const passwordRegex = /^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{6,}$/
      if (!passwordRegex.test(this.form.password)) {
        this.passwordError = 'Password must be at least 6 characters, include an uppercase letter, a number, and a special character (!@#$%^&*).'
      } else {
        this.passwordError = ''
        this.validateRetypePassword()
      }
    },
    validateRetypePassword() {
      if (this.form.password !== this.form.retype_password) {
        this.retypePasswordError = 'Passwords do not match.'
      } else {
        this.retypePasswordError = ''
      }
    },
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword
    },
    toggleRetypePasswordVisibility() {
      this.showRetypePassword = !this.showRetypePassword
    },
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    handleImageUpload(event) {
      const file = event.target.files[0]
      if (!file) {
        this.imageError = 'Please select an image.'
        this.form.user_image = null
        this.selectedFileName = ''
        return
      }

      if (!file.type.startsWith('image/')) {
        this.imageError = 'Please select a valid image file.'
        this.form.user_image = null
        this.selectedFileName = ''
        return
      }

      const maxSize = 5 * 1024 * 1024 // 5MB
      if (file.size > maxSize) {
        this.imageError = 'Image size must be less than 5MB.'
        this.form.user_image = null
        this.selectedFileName = ''
        return
      }

      const reader = new FileReader()
      reader.onload = () => {
        this.form.user_image = reader.result
        this.imageError = ''
        this.selectedFileName = file.name
      }
      reader.onerror = () => {
        this.imageError = 'Failed to read the image file.'
        this.form.user_image = null
        this.selectedFileName = ''
      }
      reader.readAsArrayBuffer(file)
    },
    async register() {
      if (this.isFormInvalid) return

      this.uploading = true
      this.uploadProgress = 0

      try {
        const formData = new FormData()
        formData.append('username', this.form.username)
        formData.append('password', this.form.password)
        formData.append('full_name', this.form.full_name)
        if (this.form.user_image) {
          const blob = new Blob([this.form.user_image], { type: 'application/octet-stream' })
          formData.append('user_image', blob)
        }

        const interval = setInterval(() => {
          if (this.uploadProgress < 90) {
            this.uploadProgress += 10
          }
        }, 200)

        const response = await axios.post('http://localhost:8000/auth/user/register', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        console.log(response)
        clearInterval(interval)
        this.uploadProgress = 100

        localStorage.setItem('access_token', response.data.access_token)
        this.alertMessage = 'Registration successful! Redirecting to home...'
        this.alertVariant = 'default'
        Swal.fire({
          icon: 'success',
          title: 'Successful',
          text: 'You have registered an account successfully!',
          confirmButtonText: 'OK'
        });
        setTimeout(() => {
          this.uploading = false
          this.$router.push('/login')
        }, 2000)
      } catch (error) {
        console.error('Đăng ký thất bại:', error)
        this.alertMessage = 'Registration failed: ' + (error.response?.data?.detail || 'Unknown error')
        this.alertVariant = 'destructive'
        this.uploading = false
        this.uploadProgress = 0
      }
    }
  }
}
</script>

<style scoped>
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