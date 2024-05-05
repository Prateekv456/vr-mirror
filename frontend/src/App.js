import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import { Button } from 'react-bootstrap';
import './App.css';

import previousIcon from './previous-icon.png'; // Import your previous icon image
import captureIcon from './capture-icon.png'; // Import your capture icon image
import nextIcon from './next-icon.png'; // Import your next icon image

function App() {
  const webcamRef = useRef(null);
  const [imageNumber, setImageNumber] = useState(0);

  const sendDataToBackend = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    // Send imageSrc and imageNumber to the backend (you can use fetch or axios)
    console.log("Sending data to backend...");
    console.log("Image number:", imageNumber);
    console.log("Image src:", imageSrc);
  }

  const changeShirt = (direction) => {
    if (direction === 'next') {
      setImageNumber(prevImageNumber => prevImageNumber + 1);
    } else if (direction === 'previous') {
      setImageNumber(prevImageNumber => prevImageNumber - 1);
    }
  }

  return (
    <div className="App">
      <h1 className="header">Virtual Reality</h1>
      <div className="webcam-container">
        <Webcam
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          className="webcam"
        />
        <div className="button-container">
          <Button onClick={() => changeShirt('previous')} variant="primary" className="navigation-button previous-button">
            <img src={previousIcon} alt="Previous" className="button-icon" />
          </Button>
          <Button onClick={sendDataToBackend} variant="primary" className="navigation-button capture-button">
            <img src={captureIcon} alt="Capture" className="button-icon" />
          </Button>
          <Button onClick={() => changeShirt('next')} variant="primary" className="navigation-button next-button">
            <img src={nextIcon} alt="Next" className="button-icon" />
          </Button>
        </div>
      </div>
    </div>
  );
}

export default App;
