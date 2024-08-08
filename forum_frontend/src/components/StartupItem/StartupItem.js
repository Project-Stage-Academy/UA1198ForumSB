import React from 'react'
import { useState } from 'react';
import './StartupItem.css'
import SendMessageForm from '../SendMessageForm/SendMessageForm';

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
            <SendMessageForm 
                show={showForm}
                handleClose={handleClose}
            />
        </li>
    );
}

export default StartupItem