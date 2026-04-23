import { registerSlonAideTools } from './src/tools.js';

const plugin = {
  id: 'slonaide',
  name: 'SlonAide',
  description: 'SlonAide 录音笔记管理插件',
  register(api) {
    registerSlonAideTools(api);
  }
};

export default plugin;