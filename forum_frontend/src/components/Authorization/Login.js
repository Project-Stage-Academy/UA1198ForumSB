import React, { useState, useEffect } from 'react';
import APIService from '../APIService/APIService';
import { useNavigate } from 'react-router-dom';
import { Input } from '../../forms/Input';

function Login() {
    const navigate = useNavigate();
    const [error, setError] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    useEffect(() => {
        if (APIService.checkTokenValid()) {
            navigate('/');
        }
    }, [navigate]);

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            await APIService.login(email, password);
            navigate('/my-cabinets');
        } catch (err) {
            const errorMessage = err?.detail || "An error occurred during login.";
            setError(errorMessage);
        }
    }

    return (
        <div className="login-form">
            <h2>Sign in</h2>
            {error && <div className="alert alert-danger">{error}</div>}
            <form onSubmit={handleLogin}>
                <Input type="email" value={email} placeholder="Enter email" onChange={setEmail} />
                <Input type="password" value={password} placeholder="Enter password" onChange={setPassword} />
                <button type="submit" className="btn btn-primary mt-3">Sign in</button>
            </form>
        </div>
    );
}

export default Login;
