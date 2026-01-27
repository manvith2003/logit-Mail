const API_BASE_URL = 'http://localhost:8000/api/v1';

export const syncEmails = async (userId, folder = 'inbox', limit = 50) => {
  const response = await fetch(`${API_BASE_URL}/emails/sync?user_id=${userId}&folder=${folder}&limit=${limit}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to sync emails');
  }
  return response.json();
};

export const getEmails = async (userId, folder = 'inbox', query = '', limit = 50, skip = 0) => {
  const url = `${API_BASE_URL}/emails/?user_id=${userId}&folder=${folder}&limit=${limit}&skip=${skip}${query ? `&q=${encodeURIComponent(query)}` : ''}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch emails');
  }
  return response.json();
};

export const sendEmail = async (userId, data) => {
  const response = await fetch(`${API_BASE_URL}/emails/send?user_id=${userId}`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to send email');
  return response.json();
};

export const starEmail = async (userId, messageId) => {
  const response = await fetch(`${API_BASE_URL}/emails/${messageId}/star?user_id=${userId}`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to star email');
  return response.json();
};

export const unstarEmail = async (userId, messageId) => {
  const response = await fetch(`${API_BASE_URL}/emails/${messageId}/unstar?user_id=${userId}`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to unstar email');
  return response.json();
};

export const trashEmail = async (userId, messageId) => {
  const response = await fetch(`${API_BASE_URL}/emails/${messageId}/trash?user_id=${userId}`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to trash email');
  return response.json();
};

export const untrashEmail = async (userId, messageId) => {
  const response = await fetch(`${API_BASE_URL}/emails/${messageId}/untrash?user_id=${userId}`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to restore email');
  return response.json();
};
