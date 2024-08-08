import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import './StartChatForm.css'
import axios from 'axios';
import {API_URL} from "../../index";
import { useState } from 'react';

function StartChatForm(props) {
    const {show, handleClose, startup} = props;
    const [message, setMessage] = useState("");
    const [statusCode, setStatusCode] = useState(0);

    const createChatAndSendFirstMessage = async (message) => {
        const token = await axios.post(`${API_URL}/users/token/`, {
            email: "borys@mail.com",
            password: "123456"
        })
        .then(resp => resp.data.access)
        .catch(err => console.log(err));

        const investor_user_id = 3;
        const investor_namespace = "investor";
        const investor_id = 1;

        const new_room = axios.post(`${API_URL}/communications/conversations/create`, {
            participants: [{
                user_id: investor_user_id,
                namespace: investor_namespace,
                namespace_id: investor_id
            },{
                user_id: startup.user,
                namespace: "startup",
                namespace_id: startup.startup_id
            }]
        }, {
            headers:{
                "Authorization": `Bearer ${token}`
            }
        })
        .then(resp => resp.data)
        .catch(err => console.log(err));

        const status = axios.post(`${API_URL}/communications/messages/send`, {
            room: new_room.id,
            author: {
                user_id: investor_user_id,
                namespace: investor_namespace,
                namespace_id: investor_id
            },
            content: message
        }, {
            headers:{
                "Authorization": `Bearer ${token}`
            }
        })
        .then(resp => resp.status)
        .catch(err => console.log(err));

        setStatusCode(Number(status));
    }

    return (
        <Modal show={show} onHide={handleClose}>
            <Modal.Header closeButton>
                <Modal.Title>
                    <div className='fs-5'>
                        Start chat with
                        <span className='text-secondary fst-italic fs-4'>
                            {` ${startup.name} `}
                        </span>
                        startup
                    </div>
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {statusCode === 201 ? 
                    <div className='success-msg'>Message has been sent.</div>
                    : null}
                <Form.Control as="textarea" placeholder='Type Message' rows={3} 
                    onChange={e => setMessage(e.target.value)}
                />
            </Modal.Body>
            <Modal.Footer>
                <Button variant="primary" onClick={() => createChatAndSendFirstMessage(message)}>
                    Send
                </Button>
                <Button variant="danger" onClick={handleClose}>
                    Close
                </Button>
            </Modal.Footer>
        </Modal>
    );
}

export default StartChatForm;