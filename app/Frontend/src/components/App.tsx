import React from 'react';
import Graphs from './Graphs/Graphs';
import './styles/App.css';

const App: React.FC = () => {
    return (
        <div className="App">
            <h1>Data Visualization Dashboard</h1>
            <Graphs />
        </div>
    );
};

export default App;