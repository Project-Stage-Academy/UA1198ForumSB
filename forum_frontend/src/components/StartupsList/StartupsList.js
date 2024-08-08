import React, { useEffect, useState } from 'react'
import axios from "axios";
import {API_URL} from "../../index";
import StartupItem from '../StartupItem/StartupItem';
import './StartupList.css'

function StartupsList() {
    const [startupsList, setStartupsList] = useState([]);

    useEffect(() => {
        const fetchStartupsList = async () => {
            const token = await axios.post(`${API_URL}/users/token/`, {
                email: "borys@mail.com",
                password: "123456"
            })
            .then(resp => resp.data.access)
            .catch(err => console.log(err));

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

export default StartupsList