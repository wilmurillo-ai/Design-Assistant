/**
 * Powpow API Client for OpenClaw
 * 
 * 用于与 Powpow 后端 API 通信的 TypeScript 客户端
 */

import axios, { AxiosError } from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

// Powpow API 基础 URL
const POWPOW_BASE_URL = process.env.POWPOW_BASE_URL || 'https://global.powpow.online';

// 配置文件路径
const CONFIG_DIR = path.join(os.homedir(), '.openclaw');
const CONFIG_PATH = path.join(CONFIG_DIR, 'powpow-config.json');

// 配置接口
interface PowpowConfig {
  username?: string;
  token?: string;
  userId?: string;
  baseUrl?: string;
  badges?: number;
}

// API 响应接口
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// 用户信息接口
interface UserInfo {
  user_id: string;
  username: string;
  nickname: string;
  avatar_url: string;
  badges: number;
  created_at?: string;
}

// 登录响应接口
interface LoginResponse extends UserInfo {
  token: string;
  expires_at: string;
}

// 数字人接口
interface DigitalHuman {
  id: string;
  name: string;
  description: string;
  avatarUrl: string;
  lng: number;
  lat: number;
  locationName: string;
  isActive: boolean;
  expiresAt: string;
  createdAt: string;
  type: string;
}

// 创建数字人响应接口
interface CreateAgentResponse extends DigitalHuman {
  badgesRemaining: number;
}

/**
 * 读取本地配置
 */
function readConfig(): PowpowConfig {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const data = fs.readFileSync(CONFIG_PATH, 'utf8');
      return JSON.parse(data);
    }
  } catch (error) {
    console.error('读取配置失败:', error);
  }
  return {};
}

/**
 * 保存本地配置
 */
function saveConfig(config: PowpowConfig): boolean {
  try {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
    return true;
  } catch (error) {
    console.error('保存配置失败:', error);
    return false;
  }
}

/**
 * 注册 Powpow 账号
 */
export async function register(
  username: string,
  nickname?: string,
  avatar_url?: string
): Promise<ApiResponse<UserInfo>> {
  try {
    const response = await axios.post<ApiResponse<UserInfo>>(
      `${POWPOW_BASE_URL}/api/openclaw/auth/register`,
      {
        username,
        nickname: nickname || username,
        avatar_url: avatar_url || '/logo.png',
      }
    );

    if (response.data.success && response.data.data) {
      // 保存配置
      const config: PowpowConfig = {
        username: response.data.data.username,
        userId: response.data.data.user_id,
        baseUrl: POWPOW_BASE_URL,
        badges: response.data.data.badges,
      };
      saveConfig(config);

      return response.data;
    }

    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse<unknown>>;
    if (axiosError.response?.data) {
      return axiosError.response.data as ApiResponse<UserInfo>;
    }
    return {
      success: false,
      error: axiosError.message || '网络错误',
    };
  }
}

/**
 * 登录 Powpow 账号
 */
export async function login(username: string): Promise<ApiResponse<LoginResponse>> {
  try {
    const response = await axios.post<ApiResponse<LoginResponse>>(
      `${POWPOW_BASE_URL}/api/openclaw/auth/login`,
      {
        username,
      }
    );

    if (response.data.success && response.data.data) {
      // 保存配置
      const config: PowpowConfig = {
        username: response.data.data.username,
        token: response.data.data.token,
        userId: response.data.data.user_id,
        baseUrl: POWPOW_BASE_URL,
        badges: response.data.data.badges,
      };
      saveConfig(config);

      return response.data;
    }

    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse<unknown>>;
    if (axiosError.response?.data) {
      return axiosError.response.data as ApiResponse<LoginResponse>;
    }
    return {
      success: false,
      error: axiosError.message || '网络错误',
    };
  }
}

/**
 * 创建数字人
 */
export async function createAgent(
  name: string,
  description: string,
  lat: number,
  lng: number,
  locationName: string,
  webhookUrl: string,
  avatarUrl?: string,
  webhookToken?: string
): Promise<ApiResponse<CreateAgentResponse>> {
  const config = readConfig();

  if (!config.token || !config.userId) {
    return {
      success: false,
      error: '未登录，请先登录或注册',
    };
  }

  // 输入验证
  if (!name || name.trim().length === 0) {
    return {
      success: false,
      error: '数字人名称不能为空',
    };
  }
  if (name.length > 100) {
    return {
      success: false,
      error: '数字人名称不能超过100个字符',
    };
  }
  if (!description || description.trim().length === 0) {
    return {
      success: false,
      error: '人设描述不能为空',
    };
  }
  // 地理位置范围验证
  if (isNaN(lat) || lat < -90 || lat > 90) {
    return {
      success: false,
      error: '纬度必须在 -90 到 90 之间',
    };
  }
  if (isNaN(lng) || lng < -180 || lng > 180) {
    return {
      success: false,
      error: '经度必须在 -180 到 180 之间',
    };
  }
  if (!locationName || locationName.trim().length === 0) {
    return {
      success: false,
      error: '位置名称不能为空',
    };
  }
  if (!webhookUrl || !webhookUrl.startsWith('http')) {
    return {
      success: false,
      error: 'Webhook URL 格式不正确，必须以 http:// 或 https:// 开头',
    };
  }

  try {
    const response = await axios.post<ApiResponse<CreateAgentResponse>>(
      `${POWPOW_BASE_URL}/api/openclaw/digital-humans`,
      {
        name,
        description,
        lat,
        lng,
        locationName,
        avatarUrl: avatarUrl || 'https://www.powpow.online/default-avatar.png',
        webhookUrl,
        webhookToken,
        userId: config.userId,
      },
      {
        headers: {
          Authorization: `Bearer ${config.token}`,
        },
      }
    );

    if (response.data.success && response.data.data) {
      // 更新徽章数量
      config.badges = response.data.data.badgesRemaining;
      saveConfig(config);
    }

    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse<unknown>>;
    if (axiosError.response?.data) {
      return axiosError.response.data as ApiResponse<CreateAgentResponse>;
    }
    return {
      success: false,
      error: axiosError.message || '网络错误',
    };
  }
}

/**
 * 获取数字人列表
 */
export async function listAgents(): Promise<ApiResponse<DigitalHuman[]>> {
  const config = readConfig();

  if (!config.token || !config.userId) {
    return {
      success: false,
      error: '未登录，请先登录或注册',
    };
  }

  try {
    const response = await axios.get<ApiResponse<DigitalHuman[]>>(
      `${POWPOW_BASE_URL}/api/openclaw/digital-humans`,
      {
        params: {
          userId: config.userId,
        },
        headers: {
          Authorization: `Bearer ${config.token}`,
        },
      }
    );

    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse<unknown>>;
    if (axiosError.response?.data) {
      return axiosError.response.data as ApiResponse<DigitalHuman[]>;
    }
    return {
      success: false,
      error: axiosError.message || '网络错误',
    };
  }
}

/**
 * 删除数字人
 */
export async function deleteAgent(agentId: string): Promise<ApiResponse<null>> {
  const config = readConfig();

  if (!config.token || !config.userId) {
    return {
      success: false,
      error: '未登录，请先登录或注册',
    };
  }

  try {
    const response = await axios.delete<ApiResponse<null>>(
      `${POWPOW_BASE_URL}/api/openclaw/digital-humans/${agentId}`,
      {
        headers: {
          Authorization: `Bearer ${config.token}`,
        },
      }
    );

    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse<unknown>>;
    if (axiosError.response?.data) {
      return axiosError.response.data as ApiResponse<null>;
    }
    return {
      success: false,
      error: axiosError.message || '网络错误',
    };
  }
}

/**
 * 获取当前登录状态
 */
export function getStatus(): { loggedIn: boolean; message: string; config?: PowpowConfig } {
  const config = readConfig();

  if (!config.token || !config.userId) {
    return {
      loggedIn: false,
      message: '未登录',
    };
  }

  return {
    loggedIn: true,
    message: '已登录',
    config,
  };
}

/**
 * 退出登录
 */
export function logout(): { success: boolean; message: string } {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      fs.unlinkSync(CONFIG_PATH);
    }
    return {
      success: true,
      message: '已退出登录',
    };
  } catch (error) {
    return {
      success: false,
      message: '退出失败: ' + error,
    };
  }
}

// 命令行接口
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'register':
      if (args.length < 2) {
        console.log('用法: npx tsx powpow-client.ts register <username> [nickname] [avatar_url]');
        process.exit(1);
      }
      const regResult = await register(args[1], args[2], args[3]);
      console.log(JSON.stringify(regResult, null, 2));
      break;

    case 'login':
      if (args.length < 2) {
        console.log('用法: npx tsx powpow-client.ts login <username>');
        process.exit(1);
      }
      const loginResult = await login(args[1]);
      console.log(JSON.stringify(loginResult, null, 2));
      break;

    case 'create-agent':
      if (args.length < 7) {
        console.log('用法: npx tsx powpow-client.ts create-agent <name> <description> <lat> <lng> <locationName> <webhookUrl> [avatarUrl] [webhookToken]');
        process.exit(1);
      }
      const createResult = await createAgent(
        args[1],
        args[2],
        parseFloat(args[3]),
        parseFloat(args[4]),
        args[5],
        args[6],
        args[7],
        args[8]
      );
      console.log(JSON.stringify(createResult, null, 2));
      break;

    case 'list-agents':
      const listResult = await listAgents();
      console.log(JSON.stringify(listResult, null, 2));
      break;

    case 'delete-agent':
      if (args.length < 2) {
        console.log('用法: npx tsx powpow-client.ts delete-agent <agentId>');
        process.exit(1);
      }
      const deleteResult = await deleteAgent(args[1]);
      console.log(JSON.stringify(deleteResult, null, 2));
      break;

    case 'status':
      const status = getStatus();
      console.log(JSON.stringify(status, null, 2));
      break;

    case 'logout':
      const logoutResult = logout();
      console.log(JSON.stringify(logoutResult, null, 2));
      break;

    default:
      console.log('Powpow OpenClaw Client');
      console.log('');
      console.log('命令:');
      console.log('  register <username> [nickname] [avatar_url]  注册账号');
      console.log('  login <username>                             登录');
      console.log('  create-agent <name> <description> <lat> <lng> <locationName> <webhookUrl> [avatarUrl] [webhookToken]  创建数字人');
      console.log('  list-agents                                  列出数字人');
      console.log('  delete-agent <agentId>                       删除数字人');
      console.log('  status                                       查看登录状态');
      console.log('  logout                                       退出登录');
      console.log('');
      console.log('示例:');
      console.log('  npx tsx powpow-client.ts register myuser "我的数字人"');
      console.log('  npx tsx powpow-client.ts create-agent "小明" "我是一个历史学家" 39.9042 116.4074 "北京" "http://localhost:18789"');
      process.exit(1);
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(console.error);
}
