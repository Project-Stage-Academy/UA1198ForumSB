import React, { useEffect, useState } from 'react'
import { API_URL } from '../../index.js';
import RoomItem from '../RoomItem/RoomItem.js';
import APIService from '../APIService/APIService.js';
import { useNavigate } from 'react-router-dom';
import NoDataInfo from '../NoDataInfo/NoDataInfo.js';

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
            {roomsList.length ? 
                <ul>
                    {roomsList.map(room => <RoomItem key={room.id} room={room}/>)}
                </ul>:
                <NoDataInfo dataName="chats" />
            }
        </div>
    );
}

export default RoomsList;