import { useState, useEffect } from 'react';
import { fetchLabs, enrollDevice } from '../api/client';

export default function RegisterDevice() {
  const [labs, setLabs] = useState([]);
  const [pcNumber, setPcNumber] = useState('');
  const [deviceName, setDeviceName] = useState('');
  const [selectedLabId, setSelectedLabId] = useState('');
  
  const [macAddress, setMacAddress] = useState('');
  
  const [statusMsg, setStatusMsg] = useState({ text: '', type: '' });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetchLabs()
      .then(data => {
        setLabs(data);
        if (data.length > 0) {
          setSelectedLabId(data[0].id.toString());
        }
      })
      .catch(() => setStatusMsg({ text: 'Failed to load labs', type: 'error' }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Client-side validation
    const newErrors = {};
    if (!pcNumber.trim()) newErrors.pcNumber = 'PC number is required';
    if (!deviceName.trim()) newErrors.deviceName = 'Device name is required';
    
    setErrors(newErrors);
    
    if (Object.keys(newErrors).length > 0) {
      return;
    }

    try {
      const device_uid = `PC-${pcNumber.trim().toUpperCase()}`;
      
      await enrollDevice({
        device_uid,
        hostname: deviceName.trim(),
        mac_address: macAddress.trim() || null,
        lab_id: selectedLabId ? parseInt(selectedLabId, 10) : null
      });
      
      setStatusMsg({ text: 'Device registered successfully', type: 'success' });
      setPcNumber('');
      setDeviceName('');
      setMacAddress('');
      // Keep selected lab as it is
    } catch (err) {
      setStatusMsg({ text: 'Failed to register device. Please try again.', type: 'error' });
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2>Register Device</h2>
      
      {statusMsg.text && (
        <div style={{ 
          padding: '10px', 
          marginBottom: '15px', 
          backgroundColor: statusMsg.type === 'success' ? '#d4edda' : '#f8d7da',
          color: statusMsg.type === 'success' ? '#155724' : '#721c24',
          borderRadius: '4px'
        }}>
          {statusMsg.text}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '5px' }}>Lab</label>
          <select 
            value={selectedLabId} 
            onChange={(e) => setSelectedLabId(e.target.value)}
            style={{ width: '100%', padding: '8px' }}
          >
            <option value="">-- Select a Lab --</option>
            {labs.map(lab => (
              <option key={lab.id} value={lab.id}>{lab.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '5px' }}>PC Number</label>
          <input 
            type="text" 
            value={pcNumber}
            onChange={(e) => setPcNumber(e.target.value)}
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
            placeholder="e.g. 101"
          />
          {errors.pcNumber && <span style={{ color: 'red', fontSize: '0.85em' }}>{errors.pcNumber}</span>}
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '5px' }}>Device Name</label>
          <input 
            type="text" 
            value={deviceName}
            onChange={(e) => setDeviceName(e.target.value)}
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
            placeholder="e.g. Lab-A-PC-101"
          />
          {errors.deviceName && <span style={{ color: 'red', fontSize: '0.85em' }}>{errors.deviceName}</span>}
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '5px' }}>MAC Address (Optional)</label>
          <input 
            type="text" 
            value={macAddress}
            onChange={(e) => setMacAddress(e.target.value)}
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
            placeholder="e.g. 00:1A:2B:3C:4D:5E"
          />
        </div>

        <button type="submit" style={{ padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Register device
        </button>
      </form>
    </div>
  );
}
