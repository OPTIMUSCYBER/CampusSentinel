import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AdminDashboard from './AdminDashboard';
import * as adminClient from '../api/adminClient';

vi.mock('../api/adminClient', () => ({
  fetchDevices: vi.fn(),
  fetchDeviceHistory: vi.fn(),
  fetchDeviceLatestSnapshot: vi.fn(),
}));

describe('AdminDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock the current date to ensure the heartbeat logic says "Online"
    vi.setSystemTime(new Date('2026-08-28T10:00:30Z'));
    
    adminClient.fetchDevices.mockResolvedValue([
      {
        id: 1,
        device_uid: 'PC-1',
        hostname: 'Lab1-PC1',
        lab_name: 'Science Lab',
        ip_address: '192.168.1.1',
        mac_address: null,
        status: 'active',
        enrolled_at: '2026-08-28T09:00:00Z',
        last_seen_at: '2026-08-28T10:00:00Z'
      }
    ]);
  });

  it('renders dashboard table and filters', async () => {
    render(<AdminDashboard />);
    
    expect(await screen.findByText('Admin Dashboard')).toBeDefined();
    expect(await screen.findByText('Lab1-PC1')).toBeDefined();
    
    // Filter
    const searchInput = screen.getByPlaceholderText('Search by lab, status, name...');
    fireEvent.change(searchInput, { target: { value: 'BOGUS' } });
    
    expect(screen.queryByText('Lab1-PC1')).toBeNull();
  });

  it('shows history and snapshot on row click', async () => {
    adminClient.fetchDeviceHistory.mockResolvedValue([
      { id: 1, event_type: 're_seen', occurred_at: '2026-08-28T10:00:00Z', detail: 'Checked in' },
      { id: 2, event_type: 'enrolled', occurred_at: '2026-08-28T09:00:00Z', detail: 'Enrolled' }
    ]);
    adminClient.fetchDeviceLatestSnapshot.mockResolvedValue({
      id: 1,
      captured_at: '2026-08-28T10:00:00Z',
      applications: ['Chrome.exe'],
      processes: ['svchost.exe']
    });
    
    render(<AdminDashboard />);
    
    const row = await screen.findByText('Lab1-PC1');
    fireEvent.click(row);
    
    expect(await screen.findByText('Lab1-PC1 Details')).toBeDefined();
    
    // Check timeline labels
    expect(await screen.findByText('Seen again')).toBeDefined();
    expect(await screen.findByText('Registered')).toBeDefined();
    
    // Check heartbeat and snapshot
    expect(await screen.findByText('Online (seen recently)')).toBeDefined();
    expect(await screen.findByText('Chrome.exe')).toBeDefined();
    expect(await screen.findByText('svchost.exe')).toBeDefined();
  });
});
