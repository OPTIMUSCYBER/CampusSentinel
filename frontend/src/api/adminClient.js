import { API_BASE_URL } from './client';

export async function fetchDevices() {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/devices`);
  if (!response.ok) {
    throw new Error('Failed to fetch devices');
  }
  return response.json();
}

export async function fetchDeviceHistory(device_uid) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/devices/${device_uid}/history`);
  if (!response.ok) {
    throw new Error('Failed to fetch device history');
  }
  return response.json();
}

export async function fetchDeviceLatestSnapshot(device_uid) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/devices/${device_uid}/snapshot`);
  if (!response.ok) {
    if (response.status === 404) return null;
    throw new Error('Failed to fetch device snapshot');
  }
  return response.json();
}
