import React from 'react'

function StartupItem(props) {
    const {startup} = props;

    return (
        <li className='startup-item'>
            {startup.name}
        </li>
    );
}

export default StartupItem