import React, { useEffect, useState } from 'react'
import axios from "axios";
import {API_URL} from "../../index";
import StartupItem from '../StartupItem/StartupItem';
import './StartupList.css'

function StartupsList() {
    const [startupsList, setStartupsList] = useState([]);

    useEffect(() => {
        const fetchStartupsList = async () => {
            const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIzMDQxODQyLCJpYXQiOjE3MjMwNDE1NDIsImp0aSI6IjI1ZDQ3ZmZmYTBiOTQzNTM4MDJhYWQzZGYzYmNiZTUyIiwidXNlcl9pZCI6M30.-5ZgF5G88FWnZCywo5bH3Z0PjddfKQOrKtWojGO6vsM";
            try {
                const response = await axios.get(
                    `${API_URL}/startups/`, {
                    headers:{
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    }
                });
                const startups = await response.data;
                setStartupsList(startups);
            }
            catch (err){
                console.log(err);
            }
        }
        fetchStartupsList();
    }, []);

    return (<>
        <h1>Startups</h1>
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

export default StartupsList