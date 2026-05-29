import client from './client'

export const toursApi = {
  getMyTours: () => client.get('/tours'),
  getPublicTours: () => client.get('/tours/public'),
  generateTour: (tourData) => client.post('/tours', tourData),
  getTourById: (tourId) => client.get(`/tours/${tourId}`),
  deleteTour: (tourId) => client.delete(`/tours/${tourId}`),
  updateTourVisibility: (tourId, visibilityData = {}) => client.patch(`/tours/${tourId}/share`, visibilityData),
  getSharedTour: (shareToken) => client.get(`/tours/shared/${shareToken}`)
}
