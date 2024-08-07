import React from 'react'
import './StartupItem.css'

function StartupItem(props) {
    const {startup} = props;

    return (
        <li className='startup-item'>
            <span className='startup-name'>{startup.name}</span>
            <button className='btn btn-primary'>Contact</button>
        </li>
    );
}

export default StartupItem