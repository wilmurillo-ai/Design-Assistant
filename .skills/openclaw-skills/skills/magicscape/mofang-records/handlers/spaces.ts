/**
 * mofang_list_spaces — 列出所有空间
 */

import { apiRequest, type HttpClientConfig } from './utils/http-client.js';

export interface SpaceItem {
  label: string;
  id: string;
}

export interface ListSpacesResult {
  success: boolean;
  message: string;
  data?: SpaceItem[];
}

function buildConfig(context: { config: Record<string, string> }): HttpClientConfig {
  return {
    baseUrl: context.config.BASE_URL,
    username: context.config.USERNAME,
    password: context.config.PASSWORD,
  };
}

function extractSpaces(data: any): SpaceItem[] {
  const items = data?.items;
  if (!Array.isArray(items)) return [];
  return items.map((item: any) => ({
    label: item.label,
    id: item.id,
  }));
}

export async function handler(
  _params: object,
  context: { config: Record<string, string> }
): Promise<ListSpacesResult> {
  const config = buildConfig(context);

  if (!config.baseUrl) {
    return { success: false, message: '未配置 BASE_URL，请先设置魔方网表服务器地址。' };
  }

  const path = '/magicflu/service/json/spaces/feed?start=0&limit=-1';
  const result = await apiRequest(config, 'GET', path);

  if (!result.success) {
    return { success: false, message: `空间列表查询失败: ${result.message}` };
  }

  const spaces = extractSpaces(result.data);

  return {
    success: true,
    message: `找到 ${spaces.length} 个空间。`,
    data: spaces,
  };
}
