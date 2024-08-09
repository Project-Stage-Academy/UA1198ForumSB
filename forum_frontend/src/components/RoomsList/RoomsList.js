import React, { useEffect, useState } from 'react'
import { API_URL } from '../../index.js';
import RoomItem from '../RoomItem/RoomItem.js';
import APIService from '../APIService/APIService.js';
import { useNavigate } from 'react-router-dom';

function RoomsList() {
    const [roomsList, setRoomsList] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const getRoomsList = async () => {
            try {
                const resp = await APIService.fetchWithAuth(`${API_URL}/communications/conversations`,
                    {}, navigate);
                setRoomsList(JSON.parse(resp.data));
            }
            catch (err) {
                console.log("getRoomsList error:", err)
            }
        }
        getRoomsList();

    }, [navigate]);
    return (
        <div>
            <ul>
                {roomsList.map(room => <RoomItem key={room.id} room={room}/>)}
            </ul>
        </div>
    );
}

export default RoomsList;