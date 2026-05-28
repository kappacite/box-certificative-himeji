/* =========================================================================
   FUTURES FONCTIONS D'AUTHENTIFICATION
   Basées sur la documentation de l'API (Endpoints /api/auth/*)
   =========================================================================

import client from './client'

export const authApi = {
  // Inscription d'un utilisateur[cite: 4]
  // POST /api/auth/register[cite: 4]
  // Payload attendu : { username, email, password }[cite: 4]
  register: (userData) => client.post('/api/auth/register', userData),

  // Connexion d'un utilisateur[cite: 4]
  // POST /api/auth/login[cite: 4]
  // Payload attendu : { email, password }[cite: 4]
  // Renvoie le token de session JWT en cas de succès[cite: 4]
  login: (credentials) => client.post('/api/auth/login', credentials),

  // Déconnexion d'un utilisateur [Auth Requise][cite: 4]
  // POST /api/auth/logout[cite: 4]
  // Aucun corps de requête, nécessite le header d'Auth[cite: 4]
  logout: () => client.post('/api/auth/logout')
}
*/