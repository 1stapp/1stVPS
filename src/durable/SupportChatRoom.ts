/**
 * Cloudflare Durable Object: 实时在线客服聊天室
 */
export class SupportChatRoom {
  private sessions = new Set<WebSocket>();

  constructor(private state: DurableObjectState) {}

  async fetch(request: Request): Promise<Response> {
    if (request.headers.get('Upgrade') !== 'websocket') {
      return new Response('Expected WebSocket', { status: 426 });
    }

    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    server.accept();
    this.sessions.add(server);

    server.addEventListener('message', (event) => {
      const msg = typeof event.data === 'string' ? event.data : '';
      const payload = JSON.stringify({
        id: crypto.randomUUID(),
        text: msg,
        ts: new Date().toISOString(),
      });
      for (const ws of this.sessions) {
        try {
          ws.send(payload);
        } catch {
          this.sessions.delete(ws);
        }
      }
    });

    server.addEventListener('close', () => {
      this.sessions.delete(server);
    });

    return new Response(null, { status: 101, webSocket: client });
  }
}
