/* =========================================================================
   VÉRIFICATION DU SERVEUR
   =========================================================================

import client from './client'

export const healthApi = {
  // Vérification de la disponibilité (Healthcheck)[cite: 4]
  // GET /api/health[cite: 4]
  // Utile pour afficher un indicateur de statut du serveur sur le frontend[cite: 4]
  checkStatus: () => client.get('/api/health')
}
*/