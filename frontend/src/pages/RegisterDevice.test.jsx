import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RegisterDevice from './RegisterDevice';
import * as client from '../api/client';

// Mock the API client
vi.mock('../api/client', () => ({
  fetchLabs: vi.fn(),
  enrollDevice: vi.fn(),
}));

describe('RegisterDevice', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    client.fetchLabs.mockResolvedValue([{ id: 1, name: 'Main Lab' }]);
  });

  it('renders the form and loads labs', async () => {
    render(<RegisterDevice />);
    
    expect(screen.getByText('Register Device')).toBeDefined();
    
    // Wait for labs to load
    await waitFor(() => {
      expect(screen.getByText('Main Lab')).toBeDefined();
    });
  });

  it('blocks submit on empty fields and shows errors', async () => {
    render(<RegisterDevice />);
    
    // Submit empty form
    fireEvent.click(screen.getByText('Register device'));
    
    // Check for validation errors
    expect(await screen.findByText('PC number is required')).toBeDefined();
    expect(await screen.findByText('Device name is required')).toBeDefined();
    
    // Ensure API was not called
    expect(client.enrollDevice).not.toHaveBeenCalled();
  });

  it('calls the enroll endpoint with the correct payload on valid submit', async () => {
    client.enrollDevice.mockResolvedValue({ id: 1, device_uid: 'PC-101' });
    
    render(<RegisterDevice />);
    
    // Wait for labs to load so the dropdown is populated
    await waitFor(() => screen.getByText('Main Lab'));
    
    // Fill out form
    fireEvent.change(screen.getByPlaceholderText('e.g. 101'), { target: { value: ' 101 ' } });
    fireEvent.change(screen.getByPlaceholderText('e.g. Lab-A-PC-101'), { target: { value: 'Test-PC' } });
    
    // Submit
    fireEvent.click(screen.getByText('Register device'));
    
    await waitFor(() => {
      expect(client.enrollDevice).toHaveBeenCalledWith({
        device_uid: 'PC-101',
        hostname: 'Test-PC',
        mac_address: null,
        lab_id: 1
      });
    });
    
    // Check success message
    expect(screen.getByText('Device registered successfully')).toBeDefined();
  });
});
