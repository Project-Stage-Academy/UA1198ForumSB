import React, { useEffect, useState } from 'react'
import axios from "axios";
import {API_URL} from "../../index";
import StartupItem from '../StartupItem/StartupItem';

function StartupsList() {
    const [startupsList, setStartupsList] = useState([]);

    useEffect(() => {
        const fetchStartupsList = async () => {
            const token = "some.jwt.token";
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
            {startupsList.length ? <ul>
                {startupsList.map(startup => {
                        return <StartupItem startup={startup} key={startup.startup_id}/>;
                    }
                )}
            </ul> : <span className='no-data'>There are no startups yet...</span>}
        </div>
    </>);
}

export default StartupsList