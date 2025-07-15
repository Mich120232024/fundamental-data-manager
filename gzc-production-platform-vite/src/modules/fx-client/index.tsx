import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Ensure this import is correct
import reportWebVitals from './reportWebVitals'; // Ensure this import is correct

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Measure performance in your app
reportWebVitals(console.log);

