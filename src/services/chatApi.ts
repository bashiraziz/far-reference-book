/**
 * Chat API client for FAR Reference Book chatbot.
 *
 * Handles all HTTP communication with the FastAPI backend.
 */

const DEFAULT_LOCAL_BACKEND_URLS = [
  'http://localhost:',
  'http://127.0.0.1:8080',
  'http://localhost:8080',
  'http://127.0.0.1:8080',
];

// Resolve backend URL from env or Docusaurus siteConfig
const getBackendUrl = (): string | undefined => {
  const env =
    typeof globalThis !== 'undefined'
      ? (globalThis as any)?.process?.env
      : undefined;

  if (env?.BACKEND_URL) {
    return env.BACKEND_URL as string;
  }
  if (env?.REACT_APP_BACKEND_URL) {
    return env.REACT_APP_BACKEND_URL as string;
  }

  if (typeof window !== 'undefined') {
    const siteConfig = (window as any).docusaurus?.siteConfig;
    if (siteConfig?.customFields?.backendUrl) {
      return siteConfig.customFields.backendUrl as string;
    }
  }

  return undefined;
};

const configuredBackendUrl = getBackendUrl();
const API_BASE_URL =
  configuredBackendUrl ?? DEFAULT_LOCAL_BACKEND_URLS[0];

const buildPreferredBaseUrls = (initial?: string): string[] => {
  const urls: string[] = [];
  if (initial) {
    urls.push(initial);
  }
  for (const fallbackUrl of DEFAULT_LOCAL_BACKEND_URLS) {
    if (!urls.includes(fallbackUrl)) {
      urls.push(fallbackUrl);
    }
  }
  return urls;
};

export interface Source {
  chunk_id: string;
  chapter: number;
  section: string;
  page?: number;
  relevance_score: number;
  excerpt: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  selected_text?: string | null;
  sources?: Source[] | null;
  token_count?: number | null;
  processing_time_ms?: number | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

export interface CreateConversationRequest {
  source?: string;
  metadata?: Record<string, any>;
}

export interface SendMessageRequest {
  content: string;
  selected_text?: string;
}

export interface ChatResponse {
  user_message: Message;
  assistant_message: Message;
}

class ChatAPI {
  private baseUrl: string;
  private preferredBaseUrls: string[];

  constructor() {
    this.preferredBaseUrls = buildPreferredBaseUrls(API_BASE_URL);
    this.baseUrl = this.preferredBaseUrls[0];
  }

  private setActiveBaseUrl(url: string) {
    this.baseUrl = url;
    this.preferredBaseUrls = [
      url,
      ...this.preferredBaseUrls.filter((candidate) => candidate !== url),
    ];
  }

  private async fetchWithFallback(
    path: string,
    options?: RequestInit
  ): Promise<Response> {
    let lastError: unknown;

    for (const baseUrl of this.preferredBaseUrls) {
      try {
        const response = await fetch(`${baseUrl}${path}`, options);

        if (baseUrl !== this.baseUrl) {
          this.setActiveBaseUrl(baseUrl);
        }

        return response;
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? new Error('Unable to reach FAR chatbot backend.');
  }

  async createConversation(
    request: CreateConversationRequest = {}
  ): Promise<Conversation> {
    const response = await this.fetchWithFallback('/conversations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to create conversation: ${response.statusText}`);
    }

    return response.json();
  }

  async getConversation(conversationId: string): Promise<Conversation> {
    const response = await this.fetchWithFallback(
      `/conversations/${conversationId}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get conversation: ${response.statusText}`);
    }

    return response.json();
  }

  async getMessages(conversationId: string): Promise<Message[]> {
    const response = await this.fetchWithFallback(
      `/conversations/${conversationId}/messages`
    );

    if (!response.ok) {
      throw new Error(`Failed to get messages: ${response.statusText}`);
    }

    return response.json();
  }

  async sendMessage(
    conversationId: string,
    request: SendMessageRequest
  ): Promise<ChatResponse> {
    // Use simplified endpoint as workaround
    const response = await this.fetchWithFallback(
      `/chat/${conversationId}/messages/simple`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `Failed to send message: ${response.statusText}`
      );
    }

    return response.json();
  }
}

export const chatApi = new ChatAPI();
