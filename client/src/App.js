// src/App.js
import React from 'react';
import Profile from './components/Profile';
import './App.css';

function App() {
  return (
    <div className="App">
      <h1>BrushUp</h1>
      <Profile userId={1} />
    </div>
  );
}

export default App;