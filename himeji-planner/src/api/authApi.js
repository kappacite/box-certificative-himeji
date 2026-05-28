import client from './client'

export const authApi = {
  login: (credentials) => client.post('/auth/login', credentials),
  register: (userData) => client.post('/auth/register', userData),
  logout: () => client.post('/auth/logout')
}
