const axios = require('axios');

async function fetchUsers() {
  try {
    const response = await axios.get('https://ada93a08cb4d.ngrok-free.app/admin/users');
    console.log('Response data:', response.data);
  } catch (error) {
    console.error('Error fetching users:', error.message);
  }
}

fetchUsers();
