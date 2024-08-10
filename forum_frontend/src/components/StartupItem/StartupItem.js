import React, { useEffect } from 'react'
import { useState } from 'react';
import './StartupItem.css'
import StartChatForm from '../StartChatForm/StartChatForm';
import { useNavigate } from 'react-router-dom';
import { API_URL } from '../../index';
import APIService from '../APIService/APIService';

function StartupItem(props) {
    const {startup} = props;
    const [showForm, setShowForm] = useState(false);
    const [isContacted, setIsContacted] = useState(false);
    const navigate = useNavigate();

    const handleClose = () => setShowForm(false);
    const handleShow = () => setShowForm(true);

    useEffect(() => {
        const getRoomsList = async () => {
            try {
                const resp = await APIService.fetchWithAuth(`${API_URL}/communications/conversations`,
                    {}, navigate);
                const roomsList = JSON.parse(resp.data).map(room => JSON.parse(room));
                console.log(roomsList);
                setIsContacted(
                    roomsList.find(room => room.name.includes(`startup_${startup.startup_id}`))
                );
            }
            catch (err) {
                console.log("getRoomsList error:", err)
            }
        }
        getRoomsList();
    }, [navigate, startup]);

    return (
        <li className='startup-item'>
            <span className='startup-name'>{startup.name}</span>
            {isContacted ? <div className='text-success fw-bold'>Contacted</div> :
                <button className='btn btn-primary' onClick={handleShow}>
                    Contact
                </button>}
            <StartChatForm 
                show={showForm}
                handleClose={handleClose}
                startup={startup}
                setIsContacted={setIsContacted}
            />
        </li>
    );
}

export default StartupItem