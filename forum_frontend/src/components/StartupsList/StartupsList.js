import React, { useEffect, useState } from 'react';
import APIService from '../APIService/APIService';
import StartupItem from '../StartupItem/StartupItem';
import { API_URL } from '../../index';
import { useNavigate } from 'react-router-dom';
import './StartupList.css';

function StartupsList() {
    const [startupsList, setStartupsList] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchStartupsList = async () => {
            try {
                const response = await APIService.fetchWithAuth(`${API_URL}/startups/`,
                    {}, navigate);
                if (!response) return;
                setStartupsList(response.data);
            } catch (err) {
                console.log("Error fetching startups", err);
            }
        };
        fetchStartupsList();
    }, [navigate]);

    return (<>
        <h1 className='mt-2 mb-3'>Startups</h1>
        <div>
            {startupsList.length ? <ul className='startups-list'>
                {startupsList.map(startup => {
                        return <StartupItem startup={startup} key={startup.startup_id}/>;
                    }
                )}
            </ul> : <span className='no-data'>There are no startups yet...</span>}
        </div>
    </>);
}

export default StartupsList;