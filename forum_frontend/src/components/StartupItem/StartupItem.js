import React from 'react'
import { useState } from 'react';
import './StartupItem.css'
import StartChatForm from '../StartChatForm/StartChatFrom';

function StartupItem(props) {
    const {startup} = props;
    const [showForm, setShowForm] = useState(false);

    const handleClose = () => setShowForm(false);
    const handleShow = () => setShowForm(true);

    return (
        <li className='startup-item'>
            <span className='startup-name'>{startup.name}</span>
            <button className='btn btn-primary' onClick={handleShow}>
                Contact
            </button>
            <StartChatForm 
                show={showForm}
                handleClose={handleClose}
                startup={startup}
            />
        </li>
    );
}

export default StartupItem