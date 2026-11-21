import { Env } from '../types';
import { getAdminSettings } from './settings';

/**
 * OVHcloud API v1 客户端 (Workers 原生 Web Crypto SHA-1 签名)
 * 文档参考: https://api.eu.ovhcloud.com/console/
 */
export class OvhClient {
  private endpoint = 'https://eu.api.ovh.com/1.0';

  constructor(private env: Env) {}

  private async sha1Hex(input: string): Promise<string> {
    const data = new TextEncoder().encode(input);
    const hashBuffer = await crypto.subtle.digest('SHA-1', data);
    return Array.from(new Uint8Array(hashBuffer))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
  }

  async request<T = unknown>(method: 'GET' | 'POST' | 'PUT' | 'DELETE', path: string, body?: unknown): Promise<T> {
    const settings = await getAdminSettings(this.env);
    const url = `${this.endpoint}${path}`;
    const timestamp = Math.floor(Date.now() / 1000).toString();
    const payload = body ? JSON.stringify(body) : '';
    const toSign = `${settings.ovhAppSecret}+${settings.ovhConsumerKey}+${method}+${url}+${payload}+${timestamp}`;
    const signature = `$1$${await this.sha1Hex(toSign)}`;

    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-Ovh-Application': settings.ovhAppKey,
        'X-Ovh-Consumer': settings.ovhConsumerKey,
        'X-Ovh-Timestamp': timestamp,
        'X-Ovh-Signature': signature,
      },
      body: payload || undefined,
    });

    if (!res.ok) {
      throw new Error(`OVH API error ${res.status}: ${await res.text()}`);
    }
    return res.json() as Promise<T>;
  }

  /** 列出账号下的裸金属服务器 */
  listDedicatedServers() {
    return this.request<string[]>('GET', '/dedicated/server');
  }

  /** 获取裸金属服务器硬件与网络详情 */
  getServerDetails(serviceName: string) {
    return this.request<Record<string, unknown>>('GET', `/dedicated/server/${serviceName}`);
  }

  /** 自动化在裸金属服务器上重装 Proxmox VE 虚拟化系统 */
  installProxmoxTemplate(serviceName: string, templateName = 'proxmox8_64', hostname?: string) {
    return this.request('POST', `/dedicated/server/${serviceName}/install/start`, {
      templateName,
      details: hostname ? { customHostname: hostname } : undefined,
    });
  }

  /** 获取分配给裸金属的 IPv4 / IPv6 地址块 */
  listServerIps(serviceName: string) {
    return this.request<string[]>('GET', `/dedicated/server/${serviceName}/ips`);
  }
}
