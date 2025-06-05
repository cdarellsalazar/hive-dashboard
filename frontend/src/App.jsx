import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
    const [connected, setConnected] = useState(false);
    const [telemetryData, setTelemetryData] = useState({});
    const [statusHistory, setStatusHistory] = useState([]);

    useEffect(() => {
        const ws = new WebSocket(`ws://${window.location.hostname}:8000/api/telemetry/ws`);

        ws.onopen = () => {
            console.log('Connected to WebSocket');
            setConnected(true);
        };

        ws.onclose = () => {
            console.log('Disconnected from WebSocket');
            setConnected(false);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setTelemetryData(data);

                setStatusHistory(prev => {
                    const newHistory = [...prev, {
                        timestamp: new Date().toISOString(),
                        ...data
                    }];
                    return newHistory.slice(-10);
                });
            } catch (error) {
                console.error('Error parsing telemetry data:', error);
            }
        };

        return () => {
            ws.close();
        };
    }, []);

    return (
        <div className="App">
            <header className="App-header">
                <h1>Drone Dashboard</h1>
                <div className="connection-status">
                    Status: { connected ?
                    <span className="connected">Connected</span> : 
                    <span className="disconnected">Disconnected</span>}
                </div>
            </header>

            <main>
                <section className="current-status">
                    <h2>Current Telemetry</h2>
                    <div className="telemetry-card">
                        <div className="metric">
                            <span className="label">Battery:</span>
                            <span className="value">{telemetryData.battery?.toFixed(2) || 'N/A'}%</span>
                        </div>
                        <div className="metric">
                            <span className="label">Altitude:</span>
                            <span className="value">{telemetryData.altitude?.toFixed(2) || 'N/A'} m</span>
                        </div>
                        <div className="metric">
                            <span className="label">Speed:</span>
                            <span className="value">{telemetryData.speed?.toFixed(2) || 'N/A'} m/s</span>
                        </div>
                        <div className="metric">
                            <span className="label">Coordinates:</span>
                            <span className="value">
                                {telemetryData.lat?.toFixed(6) || 'N/A'}, {telemetryData.lng?.toFixed(6) || 'N/A'}
                            </span>
                        </div>
                    </div>
                </section>

                <section className="history">
                    <h2>Telemetry History</h2>
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
                            {statusHistory.map((entry, index) => (
                                <tr key={index}>
                                    <td>{new Date(entry.timestamp).toLocaleDateString()}</td>
                                    <td>{entry.battery?.toFixed(2) || 'N/A'}%</td>
                                    <td>{entry.altitude?.toFixed(2) || 'N/A'} m</td>
                                    <td>{entry.speed?.toFixed(2) || 'N/A'} m/s</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </section>
            </main>
        </div>
    );
}

export default App;