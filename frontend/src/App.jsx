import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
    const [connected, setConnected] = useState(false);
    const [drones, setDrones] = useState([]);
    const [selectedDrone, setSelectedDrone] = useState(null);
    const [statusHistory, setStatusHistory] = useState({});
    const selectedDroneRef = useRef(null); 

    useEffect(() => {
        selectedDroneRef.current = selectedDrone;
    }, [selectedDrone]);
    
    useEffect(() => {
        console.log('Connecting to WebSocket...');
        const wsUrl = `ws://${window.location.hostname}:8000/api/telemetry/ws`;
        console.log(`WebSocket URL: ${wsUrl}`);
        
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log('WebSocket connected');
            setConnected(true);
        };
        
        ws.onclose = () => {
            console.log('WebSocket disconnected');
            setConnected(false);
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.drones && Array.isArray(data.drones)) {
                    console.log(`Received data for ${data.drones.length} drones`);
                    setDrones(data.drones);
                    
                    if (selectedDroneRef.current === null && data.drones.length > 0) {
                        console.log('Selecting first drone (initial load)');
                        setSelectedDrone(data.drones[0].id);
                    } else if (selectedDroneRef.current && !data.drones.find(d => d.id === selectedDroneRef.current)) {
                        console.log('Selected drone disappeared, selecting new one');
                        setSelectedDrone(data.drones.length > 0 ? data.drones[0].id : null);
                    }
                    
                    // Update history for each drone
                    const newHistory = { ...statusHistory };
                    data.drones.forEach(drone => {
                        if (!newHistory[drone.id]) {
                            newHistory[drone.id] = [];
                        }
                        newHistory[drone.id] = [
                            ...newHistory[drone.id], 
                            {...drone, timestamp: new Date()}
                        ].slice(-10); // Keep only last 10 entries
                    });
                    
                    setStatusHistory(newHistory);
                }
            } catch (error) {
                console.error('Error parsing data:', error);
            }
        };
        
        return () => {
            ws.close();
        };
    }, []);

    // Get the currently selected drone data
    const selectedDroneData = selectedDrone 
        ? drones.find(d => d.id === selectedDrone) 
        : null;
    
    // Get history for selected drone
    const selectedDroneHistory = selectedDrone && statusHistory[selectedDrone] 
        ? statusHistory[selectedDrone] 
        : [];

    return (
        <div className="App">
            <header className="App-header">
                <h1>Drone Fleet Dashboard</h1>
                <div className="connection-status">
                    Status: { connected ?
                    <span className="connected">Connected</span> : 
                    <span className="disconnected">Disconnected</span>}
                </div>
            </header>

            <main>
                <section className="drone-selector">
                    <h2>Active Drones</h2>
                    <div className="drone-cards">
                        {drones.map(drone => (
                            <div 
                                key={drone.id} 
                                className={`drone-card ${selectedDrone === drone.id ? 'selected' : ''}`}
                                onClick={() => setSelectedDrone(drone.id)}
                            >
                                <div className="drone-name">{drone.name}</div>
                                <div className="drone-status">
                                    <span className={`status-indicator ${drone.is_flying ? 'flying' : 'grounded'}`}></span>
                                    {drone.is_flying ? 'Flying' : 'Grounded'}
                                </div>
                                <div className="drone-battery">
                                    Battery: {drone.battery?.toFixed(2) || 'N/A'}%
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {selectedDroneData && (
                    <section className="current-status">
                        <h2>Current Telemetry: {selectedDroneData.name}</h2>
                        <div className="telemetry-card">
                            <div className="metric">
                                <span className="label">Battery:</span>
                                <span className="value">{selectedDroneData.battery?.toFixed(2) || 'N/A'}%</span>
                            </div>
                            <div className="metric">
                                <span className="label">Altitude:</span>
                                <span className="value">{selectedDroneData.altitude?.toFixed(2) || 'N/A'} m</span>
                            </div>
                            <div className="metric">
                                <span className="label">Speed:</span>
                                <span className="value">{selectedDroneData.speed?.toFixed(2) || 'N/A'} m/s</span>
                            </div>
                            <div className="metric">
                                <span className="label">Coordinates:</span>
                                <span className="value">
                                    {selectedDroneData.lat?.toFixed(6) || 'N/A'}, {selectedDroneData.lng?.toFixed(6) || 'N/A'}
                                </span>
                            </div>
                            <div className="metric">
                                <span className="label">Status:</span>
                                <span className="value">{selectedDroneData.is_flying ? 'Flying' : 'Grounded'}</span>
                            </div>
                        </div>
                    </section>
                )}

                {selectedDroneData && (
                    <section className="history">
                        <h2>Telemetry History: {selectedDroneData.name}</h2>
                        <table className="history-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Battery</th>
                                    <th>Altitude</th>
                                    <th>Speed</th>
                                </tr>
                            </thead>
                            <tbody>
                                {selectedDroneHistory.map((entry, index) => (
                                    <tr key={index}>
                                        <td>{new Date(entry.timestamp).toLocaleTimeString()}</td>
                                        <td>{entry.battery?.toFixed(2) || 'N/A'}%</td>
                                        <td>{entry.altitude?.toFixed(2) || 'N/A'} m</td>
                                        <td>{entry.speed?.toFixed(2) || 'N/A'} m/s</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </section>
                )}
            </main>
        </div>
    );
}

export default App;