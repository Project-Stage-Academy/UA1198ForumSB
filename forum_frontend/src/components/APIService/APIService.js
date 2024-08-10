import axios from 'axios';
import { API_URL } from "../../index";
import { jwtDecode} from 'jwt-decode';
import Cookies from 'js-cookie';

export default class APIService {
    static getAccessToken(){
        return Cookies.get('access_token');
    }

    static checkTokenExpired(token) {
        try {
            const decodedToken = jwtDecode(token);
            const currentTime = Date.now() / 1000;
            return decodedToken.exp < currentTime;
        } catch (e) {
            console.log("Failed to decode token", e);
            return true;
        }
    }

    static checkTokenValid() {
        const token = Cookies.get('access_token');
        return token && !this.checkTokenExpired(token);
    }

    static getDecodedToken() {
        const token = Cookies.get('access_token');
        if (!token) return null;
        try {
            const decodedToken = jwtDecode(token);
            return decodedToken;
        } catch (e) {
            console.log("Failed to decode token", e);
            return null;
        }
    }

    static getNamespaceInfoFromToken() {
        const decodedToken = this.getDecodedToken();
        const user_id = decodedToken.user_id;
        const namespace = decodedToken.name_space_name;
        const namespace_id = decodedToken.name_space_id;

        if (!user_id || !namespace || !namespace_id || namespace !== "investor") {
            return null;
        }

        return { user_id, namespace, namespace_id };
    }

    static async refreshToken(navigate) {
        const response = await axios.post(`${API_URL}/users/token/refresh/`, {}, {
            withCredentials: true
        }).catch((err) => {
            console.log("Failed to refresh token", err);
            navigate('/login');
        });
        return response.data.access;
    }

    static async fetchWithAuth(url, options = {}, navigate) {
        let token = Cookies.get('access_token');

        if (!token) {
            navigate('/login');
            return;
        } else if (this.checkTokenExpired(token)) {
            token = await this.refreshToken(navigate);
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
