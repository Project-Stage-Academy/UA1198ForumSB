import React, { useEffect } from 'react'
import { useState } from 'react';
import './StartupItem.css'
import StartChatForm from '../StartChatForm/StartChatForm';

function StartupItem(props) {
    const {startup, roomsList} = props;
    const [showForm, setShowForm] = useState(false);
    const [isContacted, setIsContacted] = useState(false);

    const handleClose = () => setShowForm(false);
    const handleShow = () => setShowForm(true);

    useEffect(() => {
        setIsContacted(
            !!roomsList.find(room => room.name.includes(`startup_${startup.startup_id}`))
        );
    }, [roomsList, startup]);

    return (
        <li className='startup-item'>
            <span className='startup-name'>{startup.name}</span>
            {!isContacted ? <button className='btn btn-primary' onClick={handleShow}>
                Contact
            </button> : <div className='text-success fw-bold'>contacted</div>}
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