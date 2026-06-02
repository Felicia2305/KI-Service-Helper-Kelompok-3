import client from './client';
import { mapService } from './mappers';

export const servicesApi = {
  async list() {
    const { data } = await client.get('/api/services');
    return data.map(mapService);
  },
};
