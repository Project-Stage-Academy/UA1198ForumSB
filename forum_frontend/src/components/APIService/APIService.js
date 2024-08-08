import axios from 'axios';
import { API_URL } from "../../index";

export default class APIService {
    static async RefreshToken(navigate) {
        const response = await axios.post(`${API_URL}/users/token/refresh/`, {}, {
            withCredentials: true
        }).catch((err) => {
            console.log("Failed to refresh token", err);
            navigate('/login');
        });
        return response.data.access;
    }

    static async fetchWithAuth(url, options = {}, navigate) {
        let token = await this.RefreshToken(navigate);
        if (!token) {
            navigate('/login');
            return;
        }

        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            ...options.headers,
        };

        return axios({ url, ...options, headers, withCredentials: true });
    }

    static async login(email, password) {
        try {
            const response = await axios.post(`${API_URL}/users/token/`, 
                { email, password }, { withCredentials: true });
            return response.data;
        } catch (err) {
            throw err.response.data;
        }
    }
}
