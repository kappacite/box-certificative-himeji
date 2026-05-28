import axios from 'axios'

const apiTravel = axios.create({
    baseUrl: "http://localhost:5000/",
    timeout:5000,
    headers: {}
})

export default apiTravel;