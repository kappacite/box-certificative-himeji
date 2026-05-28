/* =========================================================================
   FUTURES FONCTIONS POUR LES ITINÉRAIRES (TOURS)
   Basées sur la documentation de l'API (Endpoints /api/tours/*)
   =========================================================================

import client from './client'

export const toursApi = {
  // Lister mes itinéraires [Auth Requise][cite: 4]
  // GET /api/tours[cite: 4]
  getMyTours: () => client.get('/api/tours'),

  // Lister tous les itinéraires publics (Aucun jeton requis)[cite: 4]
  // GET /api/tours/public[cite: 4]
  getPublicTours: () => client.get('/api/tours/public'),

  // Générer et créer un itinéraire optimisé [Auth Requise][cite: 4]
  // POST /api/tours[cite: 4]
  // Payload attendu : { name, place_ids, visibility (opt) }[cite: 4]
  // Attention : Calcule l'ordre optimal pour parcourir ces points en circuit fermé[cite: 4]
  generateTour: (tourData) => client.post('/api/tours', tourData),

  // Obtenir un itinéraire spécifique [Auth Requise][cite: 4]
  // GET /api/tours/<int:tour_id>[cite: 4]
  getTourById: (tourId) => client.get(`/api/tours/${tourId}`),

  // Supprimer un itinéraire (Propriétaire uniquement) [Auth Requise][cite: 4]
  // DELETE /api/tours/<int:tour_id>[cite: 4]
  deleteTour: (tourId) => client.delete(`/api/tours/${tourId}`),

  // Basculer ou modifier la visibilité d'un itinéraire (Propriétaire uniquement) [Auth Requise][cite: 4]
  // PATCH /api/tours/<int:tour_id>/share[cite: 4]
  // Payload attendu : { visibility: "public" | "private" } ou vide pour commuter (toggle)[cite: 4]
  updateTourVisibility: (tourId, visibilityData = {}) => client.patch(`/api/tours/${tourId}/share`, visibilityData),

  // Accéder à un itinéraire partagé (Aucune authentification requise)[cite: 4]
  // GET /api/tours/shared/<string:share_token>[cite: 4]
  // Permet à n'importe quel internaute d'accéder via l'UUID de partage[cite: 4]
  getSharedTour: (shareToken) => client.get(`/api/tours/shared/${shareToken}`)
}
*/