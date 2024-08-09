import React, { useEffect, useState } from 'react'
import Cookies from 'js-cookie';
import axios from 'axios';
import { API_URL } from '../../index.js';
import RoomItem from '../RoomItem/RoomItem.js';

function RoomsList() {
    const [roomsList, setRoomsList] = useState([]);

    useEffect(() => {
        const access_token = Cookies.get('access_token');

        const getRoomsList = async () => {
            try {
                const resp = await axios.get(`${API_URL}/communications/conversations`, {
                    withCredentials: true,
                    headers: {
                        "Authorization": `Bearer ${access_token}`
                    }
                });
                setRoomsList(JSON.parse(resp.data));
            }
            catch (err) {
                console.log("getRoomsList error:", err)
            }
        }
        getRoomsList();

    }, []);
    return (
        <div>
            <ul>
                {roomsList.map(room => <RoomItem key={room.id} room={room}/>)}
            </ul>
        </div>
    );
}

export default RoomsList;