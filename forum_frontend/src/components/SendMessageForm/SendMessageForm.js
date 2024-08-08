import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import './SendMessageForm.css'

function SendMessageForm(props) {
    const {show, handleClose} = props;

    return (
        <Modal show={show} onHide={handleClose}>
            <Modal.Header closeButton>
                <Modal.Title>Modal heading</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <div className='chat'>
                    Chat
                </div>
                <Form.Control as="textarea" placeholder='Type Message' rows={3}/>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="primary">
                    Send
                </Button>
                <Button variant="danger" onClick={handleClose}>
                    Close
                </Button>
            </Modal.Footer>
        </Modal>
    );
}

export default SendMessageForm;