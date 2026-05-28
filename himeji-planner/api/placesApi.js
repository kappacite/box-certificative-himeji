/* =========================================================================
   FUTURES FONCTIONS POUR LES LIEUX
   Basées sur la documentation de l'API (Endpoints /api/places/*)
   =========================================================================

import client from './client'

export const placesApi = {
  // Lister mes lieux (personnels) [Auth Requise][cite: 4]
  // GET /api/places[cite: 4]
  getMyPlaces: () => client.get('/api/places'),

  // Lister tous les lieux publics (aucune authentification requise)[cite: 4]
  // GET /api/places/public[cite: 4]
  getPublicPlaces: () => client.get('/api/places/public'),

  // Créer un lieu [Auth Requise][cite: 4]
  // POST /api/places[cite: 4]
  // Payload attendu : { name, latitude (opt), longitude (opt), visibility (opt) }[cite: 4]
  // Note : Si les coordonnées sont omises, l'API géocode le nom automatiquement[cite: 4]
  createPlace: (placeData) => client.post('/api/places', placeData),

  // Obtenir les détails d'un lieu spécifique [Auth Requise][cite: 4]
  // GET /api/places/<int:place_id>[cite: 4]
  getPlaceById: (placeId) => client.get(`/api/places/${placeId}`),

  // Modifier un lieu (Propriétaire uniquement) [Auth Requise][cite: 4]
  // PUT /api/places/<int:place_id>[cite: 4]
  updatePlace: (placeId, updateData) => client.put(`/api/places/${placeId}`, updateData),

  // Supprimer un lieu (Propriétaire uniquement) [Auth Requise][cite: 4]
  // DELETE /api/places/<int:place_id>[cite: 4]
  deletePlace: (placeId) => client.delete(`/api/places/${placeId}`)
}
*/