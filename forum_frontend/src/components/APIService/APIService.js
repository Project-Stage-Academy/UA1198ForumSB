import axios from 'axios';
import { API_URL } from "../../index";
import { jwtDecode} from 'jwt-decode';
import Cookies from 'js-cookie';

export default class APIService {    
    static GetAccessToken() {
        return Cookies.get('access_token');
    }

    static IsTokenExpired(token) {
        try {
            const decodedToken = jwtDecode(token);
            const currentTime = Date.now() / 1000;
            return decodedToken.exp < currentTime;
        } catch (e) {
            console.log("Failed to decode token", e);
            return true;
        }
    }

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
        let token = this.GetAccessToken();

        if (!token) {
            navigate('/login');
            return;
        } else if (this.IsTokenExpired(token)) {
            token = await this.RefreshToken(navigate);
            if (!token) {
                navigate('/login');
                return;
            }
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
            const response = await axios.post(`${API_URL}/users/login/`, 
                { email, password }, { withCredentials: true });
            return response.data;
        } catch (err) {
            throw err.response.data;
        }
    }
}
