import React, { useEffect, useState } from 'react';
import APIService from '../APIService/APIService';
import StartupItem from '../StartupItem/StartupItem';
import { API_URL } from '../../index';
import { useNavigate } from 'react-router-dom';
import './StartupList.css';
import NoDataInfo from '../NoDataInfo/NoDataInfo';

function StartupsList() {
    const [startupsList, setStartupsList] = useState([]);
    const [roomsList, setRoomsList] = useState([]);
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
        const getRoomsList = async () => {
            try {
                const resp = await APIService.fetchWithAuth(`${API_URL}/communications/conversations`,
                    {}, navigate);
                setRoomsList(JSON.parse(resp.data).map(room => JSON.parse(room)));
                // console.log(JSON.parse(resp.data).map(room => JSON.parse(room)));
            }
            catch (err) {
                console.log("getRoomsList error:", err)
            }
        }
        fetchStartupsList();
        getRoomsList();
    }, [navigate]);

    return (<>
        <h1 className='mt-2 mb-3'>Startups</h1>
        <div>
            {startupsList.length ? <ul className='startups-list'>
                {startupsList.map(startup => {
                    return <StartupItem 
                        key={startup.startup_id}
                        startup={startup}
                        roomsList={roomsList}
                    />;}
                )}
            </ul> : <NoDataInfo dataName="startups" />}
        </div>
    </>);
}

export default StartupsList;