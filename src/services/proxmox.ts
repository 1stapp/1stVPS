/**
 * Proxmox VE REST API 客户端 (KVM/QEMU + Cloud-Init)
 * 文档参考: https://pve.proxmox.com/pve-docs/api-viewer/
 */
export interface CreateVmParams {
  vmid: number;
  name: string;
  cores: number;
  memoryMb: number;
  diskGb: number;
  templateVmid: number; // 预先准备好的 Cloud-Init 基础镜像 VMID
  ipCidr: string;       // e.g. 51.89.10.22/24
  gateway: string;      // e.g. 51.89.10.254
  rootPassword: string;
}

export class ProxmoxClient {
  constructor(private pveHost: string, private apiToken: string) {}

  private async request<T = unknown>(method: string, path: string, form?: Record<string, string | number>): Promise<T> {
    const url = `${this.pveHost.replace(/\/$/, '')}/api2/json${path}`;
    const headers: Record<string, string> = {
      Authorization: `PVEAPIToken=${this.apiToken}`,
    };

    let body: string | undefined;
    if (form) {
      headers['Content-Type'] = 'application/x-www-form-urlencoded';
      const record: Record<string, string> = {};
      for (const [k, v] of Object.entries(form)) {
        record[k] = String(v);
      }
      body = new URLSearchParams(record).toString();
    }

    const res = await fetch(url, { method, headers, body });
    if (!res.ok) {
      throw new Error(`Proxmox API ${method} ${path} failed (${res.status}): ${await res.text()}`);
    }
    const json = (await res.json()) as { data: T };
    return json.data;
  }

  /** 从 Cloud-Init 模板克隆并配置独立 VPS */
  async provisionKvmVps(node: string, params: CreateVmParams) {
    // 1. Clone template
    await this.request('POST', `/nodes/${node}/qemu/${params.templateVmid}/clone`, {
      newid: params.vmid,
      name: params.name,
      full: 1,
    });

    // 2. Configure CPU, RAM, Cloud-Init IP & password
    await this.request('PUT', `/nodes/${node}/qemu/${params.vmid}/config`, {
      cores: params.cores,
      memory: params.memoryMb,
      ipconfig0: `ip=${params.ipCidr},gw=${params.gateway}`,
      ciuser: 'root',
      cipassword: params.rootPassword,
      agent: 'enabled=1',
    });

    // 3. Resize NVMe disk
    await this.request('PUT', `/nodes/${node}/qemu/${params.vmid}/resize`, {
      disk: 'scsi0',
      size: `${params.diskGb}G`,
    });

    // 4. Boot VM
    return this.powerAction(node, params.vmid, 'start');
  }

  powerAction(node: string, vmid: number, action: 'start' | 'stop' | 'reboot' | 'reset') {
    return this.request('POST', `/nodes/${node}/qemu/${vmid}/status/${action}`);
  }

  getVmStatus(node: string, vmid: number) {
    return this.request<{ status: string; cpu: number; mem: number; maxmem: number; netin: number; netout: number }>(
      'GET',
      `/nodes/${node}/qemu/${vmid}/status/current`
    );
  }

  getNodeStatus(node: string) {
    return this.request<Record<string, unknown>>('GET', `/nodes/${node}/status`);
  }
}
