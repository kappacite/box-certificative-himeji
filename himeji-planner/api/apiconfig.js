import axios from 'axios'

const apiTravel = axios.create({
    baseUrl: "http://localhost:5000/api/",
    timeout:5000,
    headers: {}
})

export default apiTravel;