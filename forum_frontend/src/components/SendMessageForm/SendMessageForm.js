import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import './SendMessageForm.css'

function SendMessageForm(props) {
    const {show, handleClose} = props;

    return (
        <Modal show={show} onHide={handleClose}>
            <Modal.Header closeButton>
                <Modal.Title>Modal heading</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                Woohoo, you are reading this text in a modal!
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