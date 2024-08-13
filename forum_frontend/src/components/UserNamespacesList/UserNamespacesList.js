import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL } from '../../index';
import APIService from '../APIService/APIService';
import Button from 'react-bootstrap/Button';

function UserNamespacesList() {
    const [investors, setInvestors] = useState([]);
    const [startups, setStartups] = useState([]);
    const [error, setError] = useState("");
    const [selectedNamespace, setSelectedNamespace] = useState({id: 0, name: ''});
    const navigate = useNavigate();

    useEffect(() => {
        const fetchNamespaces = async () => {
            try {
                const token = APIService.getDecodedToken();
                if (token) {
                    setSelectedNamespace({id: token.name_space_id, name: token.name_space_name});
                    const user_id = token.user_id;
                    const investorResponse = await APIService.fetchWithAuth(
                        `${API_URL}/users/${user_id}/investors/`, {}, navigate);
                    if (!investorResponse) return;
                    setInvestors(investorResponse.data);

                    const startupResponse = await APIService.fetchWithAuth(
                        `${API_URL}/users/${user_id}/startups/`, {}, navigate);
                    if (!startupResponse) return;
                    setStartups(startupResponse.data);
                } else {
                    navigate('/login');
                }
            } catch (err) {
                console.error("Error fetching namespaces", err);
                setError("Failed to load cabinets.");
            }
        };

        fetchNamespaces();
    }, [navigate]);

    const selectNamespace = async (name_space_id, name_space_name) => {
        try {
            await APIService.fetchWithAuth(`${API_URL}/users/select-namespace/`, {
                method: 'POST',
                data: { name_space_id, name_space_name },
            }, navigate);
            setSelectedNamespace({id: name_space_id, name: name_space_name});
        } catch (err) {
            console.error("Error selecting namespace", err);
            setError("Failed to select cabinet.");
        }
    };

    return (
        <div>
            {error && <div className="alert alert-danger">{error}</div>}
            <h2>Select Your Cabinet</h2>
            <div className="row">
                <div className="col-lg-12 col-md-12">
                    <h3>Investors</h3>
                    <div className="row">
                        {investors.length ? (
                            investors.map((investor) => (
                                <div key={investor.investor_id} className="col-lg-2 col-md-6 mt-4 mb-4 text-center">
                                    <div className="position-relative">
                                        <Button 
                                            variant={
                                                selectedNamespace.id === investor.investor_id && 
                                                selectedNamespace.name === 'investor' ? 
                                                "success" : "primary"
                                            } 
                                            onClick={() => selectNamespace(investor.investor_id, 'investor')}
                                        >
                                            {selectedNamespace.id === investor.investor_id && 
                                            selectedNamespace.name === 'investor' ? 
                                            "Selected" : "Select"} {investor.investor_id} 
                                        </Button>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p>You have no investor cabinets yet.</p>
                        )}
                    </div>
                </div>
                <div className="col-lg-12 col-md-12">
                    <h3>Startups</h3>
                    <div className="row">
                        {startups.length ? (
                            startups.map((startup) => (
                                <div key={startup.startup_id} className="col-lg-2 col-md-6 mt-4 mb-4 text-center">
                                    <div className="position-relative">
                                        <Button 
                                            variant={
                                                selectedNamespace.id === startup.startup_id && 
                                                selectedNamespace.name === 'startup' ? 
                                                "success" : "primary"
                                            } 
                                            onClick={() => selectNamespace(startup.startup_id, 'startup')}
                                        >
                                            {selectedNamespace.id === startup.startup_id && 
                                            selectedNamespace.name === 'startup' ? 
                                            "Selected" : "Select"} {startup.startup_id}
                                        </Button>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p>You have no startup cabinets yet.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default UserNamespacesList;