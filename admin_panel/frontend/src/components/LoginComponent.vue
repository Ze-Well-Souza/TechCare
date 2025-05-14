<template>
  <div class="login-container">
    <el-form 
      ref="loginForm" 
      :model="loginModel" 
      :rules="loginRules" 
      class="login-form"
      @submit.prevent="handleLogin"
    >
      <h2>TechCare - Painel Administrativo</h2>
      
      <el-form-item prop="username">
        <el-input 
          v-model="loginModel.username" 
          placeholder="Usuário" 
          prefix-icon="User"
        />
      </el-form-item>
      
      <el-form-item prop="password">
        <el-input 
          v-model="loginModel.password" 
          type="password" 
          placeholder="Senha" 
          show-password
          prefix-icon="Lock"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button 
          type="primary" 
          native-type="submit" 
          :loading="loading"
          class="login-button"
        >
          Entrar
        </el-button>
      </el-form-item>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </el-form>
  </div>
</template>

<script>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import AuthService from '@/services/auth.service';

export default {
  name: 'LoginComponent',
  setup() {
    const router = useRouter();
    const loading = ref(false);
    const error = ref(null);

    const loginModel = reactive({
      username: '',
      password: ''
    });

    const loginRules = {
      username: [
        { required: true, message: 'Por favor, insira o usuário', trigger: 'blur' }
      ],
      password: [
        { required: true, message: 'Por favor, insira a senha', trigger: 'blur' }
      ]
    };

    const handleLogin = async () => {
      error.value = null;
      loading.value = true;

      try {
        const response = await AuthService.login(
          loginModel.username, 
          loginModel.password
        );

        switch(response.user_role) {
          case 'admin_master':
            router.push('/admin/dashboard');
            break;
          case 'admin_tecnico':
            router.push('/tecnico/dashboard');
            break;
          case 'visualizador':
            router.push('/visualizador/dashboard');
            break;
          default:
            error.value = 'Função de usuário não reconhecida';
        }
      } catch (err) {
        error.value = err.response?.data?.msg || 'Erro de autenticação';
      } finally {
        loading.value = false;
      }
    };

    return {
      loginModel,
      loginRules,
      loading,
      error,
      handleLogin
    };
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.login-form {
  width: 400px;
  padding: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.login-button {
  width: 100%;
  margin-top: 15px;
}

.error-message {
  color: red;
  text-align: center;
  margin-top: 10px;
}
</style>
