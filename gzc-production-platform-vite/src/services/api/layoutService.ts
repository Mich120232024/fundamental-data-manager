import axios from 'axios';
import { Layout } from 'react-grid-layout';
import { LayoutComponent } from '@store/layoutStore';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface LayoutData {
  id: string;
  name: string;
  layouts: Record<string, Layout[]>;
  components: LayoutComponent[];
  userId?: string;
  createdAt: string;
  updatedAt: string;
}

class LayoutService {
  private baseUrl = `${API_URL}/api/layouts`;

  async getLayouts(): Promise<LayoutData[]> {
    const response = await axios.get(this.baseUrl);
    return response.data;
  }

  async getLayout(id: string): Promise<LayoutData> {
    try {
      const response = await axios.get(`${this.baseUrl}/${id}`);
      return response.data;
    } catch (error) {
      // Return default layout if not found
      return {
        id,
        name: 'Default Layout',
        layouts: {},
        components: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    }
  }

  async saveLayout(id: string, data: Partial<LayoutData>): Promise<LayoutData> {
    const response = await axios.put(`${this.baseUrl}/${id}`, data);
    return response.data;
  }

  async createLayout(data: Omit<LayoutData, 'id' | 'createdAt' | 'updatedAt'>): Promise<LayoutData> {
    const response = await axios.post(this.baseUrl, data);
    return response.data;
  }

  async deleteLayout(id: string): Promise<void> {
    await axios.delete(`${this.baseUrl}/${id}`);
  }
}

export const layoutService = new LayoutService();