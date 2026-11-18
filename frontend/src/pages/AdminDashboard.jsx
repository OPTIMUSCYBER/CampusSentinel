import { useState, useEffect } from 'react';
import { fetchDevices, fetchDeviceHistory, fetchDeviceLatestSnapshot } from '../api/adminClient';

export default function AdminDashboard() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [history, setHistory] = useState([]);
  const [snapshot, setSnapshot] = useState(null);

  useEffect(() => {
    loadDevices();
    const interval = setInterval(loadDevices, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  const loadDevices = async () => {
    try {
      const data = await fetchDevices();
      setDevices(data);
    } catch (err) {
      setError('Failed to load devices');
    } finally {
      setLoading(false);
    }
  };

  const handleRowClick = async (device) => {
    setSelectedDevice(device);
    setHistory([]);
    setSnapshot(null);
    try {
      const [histData, snapData] = await Promise.all([
        fetchDeviceHistory(device.device_uid).catch(() => []),
        fetchDeviceLatestSnapshot(device.device_uid).catch(() => null)
      ]);
      setHistory(histData);
      setSnapshot(snapData);
    } catch (err) {
      console.error(err);
    }
  };

  const filteredDevices = devices.filter(d => 
    (d.lab_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (d.status || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (d.hostname || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (d.device_uid || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatEventName = (type) => {
    if (type === 'enrolled') return 'Registered';
    if (type === 're_seen') return 'Seen again';
    if (type === 'status_changed') return 'Status changed';
    return type;
  };

  const isOnline = (lastSeenAt) => {
    if (!lastSeenAt) return false;
    const diffSeconds = (new Date() - new Date(lastSeenAt)) / 1000;
    return diffSeconds < 90; // Green if seen in last 90s
  };

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div style={{ display: 'flex', fontFamily: 'sans-serif', height: '100vh' }}>
      <div style={{ flex: selectedDevice ? 2 : 1, padding: '20px', borderRight: '1px solid #ccc' }}>
        <h2>Admin Dashboard</h2>
        
        <input 
          type="text" 
          placeholder="Search by lab, status, name..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          style={{ padding: '8px', marginBottom: '20px', width: '300px' }}
        />

        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
              <th style={{ padding: '10px' }}>Device Name</th>
              <th style={{ padding: '10px' }}>PC Number</th>
              <th style={{ padding: '10px' }}>Lab</th>
              <th style={{ padding: '10px' }}>IP Address</th>
              <th style={{ padding: '10px' }}>MAC Address</th>
              <th style={{ padding: '10px' }}>Status</th>
              <th style={{ padding: '10px' }}>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {filteredDevices.map(d => (
              <tr 
                key={d.id} 
                onClick={() => handleRowClick(d)}
                style={{ 
                  borderBottom: '1px solid #ddd', 
                  cursor: 'pointer',
                  backgroundColor: selectedDevice?.id === d.id ? '#e6f7ff' : 'transparent'
                }}
              >
                <td style={{ padding: '10px' }}>
                  <span style={{ 
                    display: 'inline-block', 
                    width: '8px', 
                    height: '8px', 
                    borderRadius: '50%', 
                    backgroundColor: isOnline(d.last_seen_at) ? 'green' : 'red',
                    marginRight: '8px'
                  }}></span>
                  {d.hostname || '-'}
                </td>
                <td style={{ padding: '10px' }}>{d.device_uid}</td>
                <td style={{ padding: '10px' }}>{d.lab_name || '-'}</td>
                <td style={{ padding: '10px' }}>{d.ip_address || '-'}</td>
                <td style={{ padding: '10px' }}>{d.mac_address || '-'}</td>
                <td style={{ padding: '10px' }}>{d.status}</td>
                <td style={{ padding: '10px' }}>{d.last_seen_at ? new Date(d.last_seen_at).toLocaleString() : '-'}</td>
              </tr>
            ))}
            {filteredDevices.length === 0 && (
              <tr><td colSpan="7" style={{ padding: '10px', textAlign: 'center' }}>No devices found.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedDevice && (
        <div style={{ flex: 1, padding: '20px', backgroundColor: '#fafafa', overflowY: 'auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>{selectedDevice.hostname} Details</h3>
            <button onClick={() => setSelectedDevice(null)} style={{ padding: '5px 10px', cursor: 'pointer' }}>Close</button>
          </div>
          
          <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#fff', border: '1px solid #eee', borderRadius: '4px' }}>
            <p><strong>PC Number:</strong> {selectedDevice.device_uid}</p>
            <p><strong>Lab:</strong> {selectedDevice.lab_name || 'Unassigned'}</p>
            <p><strong>Status:</strong> {selectedDevice.status}</p>
            <p><strong>Registered On:</strong> {new Date(selectedDevice.enrolled_at).toLocaleString()}</p>
            <p>
              <strong>Heartbeat:</strong>{' '}
              <span style={{ color: isOnline(selectedDevice.last_seen_at) ? 'green' : 'red' }}>
                {isOnline(selectedDevice.last_seen_at) ? 'Online (seen recently)' : 'Offline'}
              </span>
            </p>
          </div>

          <h4>Currently Running</h4>
          {snapshot ? (
            <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#fff', border: '1px solid #eee', borderRadius: '4px' }}>
              <p style={{ fontSize: '0.85em', color: '#666', marginTop: 0 }}>
                As of {new Date(snapshot.captured_at).toLocaleString()}
              </p>
              
              <strong>Applications:</strong>
              {snapshot.applications.length > 0 ? (
                <ul style={{ margin: '5px 0 15px', paddingLeft: '20px' }}>
                  {snapshot.applications.map(app => <li key={app}>{app}</li>)}
                </ul>
              ) : <p style={{ margin: '5px 0 15px' }}>None detected</p>}
              
              <strong>Background Processes:</strong>
              {snapshot.processes.length > 0 ? (
                <ul style={{ margin: '5px 0 0', paddingLeft: '20px', fontSize: '0.9em', color: '#444' }}>
                  {snapshot.processes.slice(0, 20).map(p => <li key={p}>{p}</li>)}
                  {snapshot.processes.length > 20 && <li>...and {snapshot.processes.length - 20} more</li>}
                </ul>
              ) : <p style={{ margin: '5px 0 0' }}>None detected</p>}
            </div>
          ) : (
            <p>No agent snapshot received yet.</p>
          )}

          <h4>History Timeline</h4>
          {history.length === 0 ? (
            <p>Loading history...</p>
          ) : (
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {history.map(evt => (
                <li key={evt.id} style={{ padding: '10px 0', borderBottom: '1px solid #eee' }}>
                  <strong>{formatEventName(evt.event_type)}</strong>
                  <div style={{ color: '#666', fontSize: '0.9em' }}>
                    {new Date(evt.occurred_at).toLocaleString()}
                  </div>
                  {evt.detail && <div style={{ marginTop: '5px', fontSize: '0.9em' }}>{evt.detail}</div>}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
