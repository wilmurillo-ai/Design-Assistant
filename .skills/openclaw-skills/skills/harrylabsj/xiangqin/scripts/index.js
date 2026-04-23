/**
 * Xiangqin - Blind Date Assistant
 * Help singles efficiently find matches
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

class BlindDateAssistant {
  constructor() {
    this.dataDir = path.join(os.homedir(), '.openclaw', 'skills-data', 'xiangqin');
    this.ensureDir();
    
    this.currentUser = null;
    this.profiles = this.loadProfiles();
    this.matches = this.loadMatches();
    this.conversations = this.loadConversations();
  }

  ensureDir() {
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
  }

  // ========== Data Persistence ==========
  
  loadProfiles() {
    const file = path.join(this.dataDir, 'profiles.json');
    if (fs.existsSync(file)) {
      return JSON.parse(fs.readFileSync(file, 'utf-8'));
    }
    return {};
  }

  saveProfiles() {
    const file = path.join(this.dataDir, 'profiles.json');
    fs.writeFileSync(file, JSON.stringify(this.profiles, null, 2));
  }

  loadMatches() {
    const file = path.join(this.dataDir, 'matches.json');
    if (fs.existsSync(file)) {
      return JSON.parse(fs.readFileSync(file, 'utf-8'));
    }
    return {};
  }

  saveMatches() {
    const file = path.join(this.dataDir, 'matches.json');
    fs.writeFileSync(file, JSON.stringify(this.matches, null, 2));
  }

  loadConversations() {
    const file = path.join(this.dataDir, 'conversations.json');
    if (fs.existsSync(file)) {
      return JSON.parse(fs.readFileSync(file, 'utf-8'));
    }
    return {};
  }

  saveConversations() {
    const file = path.join(this.dataDir, 'conversations.json');
    fs.writeFileSync(file, JSON.stringify(this.conversations, null, 2));
  }

  // ========== Profile Management ==========

  /**
   * Create/Update Profile
   */
  createProfile(userId, profile) {
    const now = new Date().toISOString();
    
    const newProfile = {
      userId,
      createdAt: this.profiles[userId]?.createdAt || now,
      updatedAt: now,
      
      // Basic Info
      basicInfo: {
        nickname: profile.nickname,
        gender: profile.gender,
        birthYear: profile.birthYear,
        age: new Date().getFullYear() - profile.birthYear,
        height: profile.height,
        weight: profile.weight,
        location: profile.location,
        hometown: profile.hometown,
        education: profile.education,
        occupation: profile.occupation,
        income: profile.income,
        maritalStatus: profile.maritalStatus || 'single'
      },
      
      // About Me
      aboutMe: {
        personality: profile.personality || [],
        hobbies: profile.hobbies || [],
        lifestyle: profile.lifestyle,
        values: profile.values,
        selfDescription: profile.selfDescription
      },
      
      // 择偶标准
      preferences: {
        ageRange: profile.ageRange || (() => {
          const currentAge = new Date().getFullYear() - profile.birthYear;
          return {
            min: Math.max(18, currentAge - 5),
            max: currentAge + 3
          };
        })(),
        heightRange: profile.heightRange,
        locationPreference: profile.locationPreference,
        educationPreference: profile.educationPreference,
        incomePreference: profile.incomePreference,
        otherRequirements: profile.otherRequirements || []
      },
      
      // 照片
      photos: profile.photos || [],
      
      // 隐私设置
      privacy: {
        showRealName: false,
        showPhone: false,
        showWechat: false,
        ...profile.privacy
      },
      
      // 状态
      status: 'active',
      verified: false
    };
    
    this.profiles[userId] = newProfile;
    this.saveProfiles();
    
    return {
      success: true,
      profile: newProfile,
      message: '资料已保存',
      completeness: this.calculateCompleteness(newProfile)
    };
  }

  /**
   * Calculate Profile Completeness
   */
  calculateCompleteness(profile) {
    let score = 0;
    const maxScore = 100;
    
    // Basic Info 40分
    if (profile.basicInfo.nickname) score += 5;
    if (profile.basicInfo.gender) score += 5;
    if (profile.basicInfo.birthYear) score += 5;
    if (profile.basicInfo.height) score += 5;
    if (profile.basicInfo.location) score += 5;
    if (profile.basicInfo.education) score += 5;
    if (profile.basicInfo.occupation) score += 5;
    if (profile.basicInfo.income) score += 5;
    
    // About Me 30分
    if (profile.aboutMe.hobbies?.length > 0) score += 10;
    if (profile.aboutMe.selfDescription?.length > 20) score += 10;
    if (profile.aboutMe.values) score += 10;
    
    // 择偶标准 20分
    if (profile.preferences.ageRange) score += 5;
    if (profile.preferences.locationPreference) score += 5;
    if (profile.preferences.educationPreference) score += 5;
    if (profile.preferences.otherRequirements?.length > 0) score += 5;
    
    // 照片 10分
    if (profile.photos?.length > 0) score += 10;
    
    return {
      score,
      maxScore,
      percentage: Math.round((score / maxScore) * 100),
      level: score >= 80 ? '优秀' : score >= 60 ? '良好' : score >= 40 ? '一般' : '需完善'
    };
  }

  getProfile(userId) {
    return this.profiles[userId] || null;
  }

  // ========== 智能匹配 ==========

  /**
   * Find Matches
   */
  findMatches(userId, options = {}) {
    const myProfile = this.profiles[userId];
    if (!myProfile) {
      return { success: false, error: '请先完善个人资料' };
    }
    
    const { limit = 10, filters = {} } = options;
    const matches = [];
    
    for (const [otherId, otherProfile] of Object.entries(this.profiles)) {
      if (otherId === userId) continue;
      if (otherProfile.status !== 'active') continue;
      if (otherProfile.basicInfo.gender === myProfile.basicInfo.gender) continue;
      
      // Calculate Match Score
      const matchScore = this.calculateMatchScore(myProfile, otherProfile);
      
      // 应用额外筛选
      if (filters.minAge && otherProfile.basicInfo.age < filters.minAge) continue;
      if (filters.maxAge && otherProfile.basicInfo.age > filters.maxAge) continue;
      if (filters.location && !otherProfile.basicInfo.location.includes(filters.location)) continue;
      if (filters.education && otherProfile.basicInfo.education !== filters.education) continue;
      
      matches.push({
        userId: otherId,
        profile: this.sanitizeProfile(otherProfile),
        matchScore,
        matchDetails: matchScore.details
      });
    }
    
    // 按匹配度排序
    matches.sort((a, b) => b.matchScore.total - a.matchScore.total);
    
    return {
      success: true,
      total: matches.length,
      matches: matches.slice(0, limit),
      myProfile: {
        completeness: this.calculateCompleteness(myProfile),
        preferences: myProfile.preferences
      }
    };
  }

  /**
   * Calculate Match Score评分
   */
  calculateMatchScore(profileA, profileB) {
    let totalScore = 0;
    const details = {};
    
    const prefsA = profileA.preferences;
    const prefsB = profileB.preferences;
    const basicA = profileA.basicInfo;
    const basicB = profileB.basicInfo;
    
    // 年龄匹配 20分
    const ageDiff = Math.abs(basicA.age - basicB.age);
    const ageScore = ageDiff <= 2 ? 20 : ageDiff <= 5 ? 15 : ageDiff <= 8 ? 10 : 5;
    totalScore += ageScore;
    details.age = { score: ageScore, note: `年龄差${ageDiff}years` };
    
    // 身high匹配 10分
    let heightScore = 10;
    if (basicA.gender === 'male' && basicA.height - basicB.height >= 10) heightScore = 10;
    else if (basicA.gender === 'female' && basicB.height - basicA.height >= 10) heightScore = 10;
    else heightScore = 5;
    totalScore += heightScore;
    details.height = { score: heightScore };
    
    // 地域匹配 20分
    let locationScore = 0;
    if (basicA.location === basicB.location) locationScore = 20;
    else if (basicA.location.split(' ')[0] === basicB.location.split(' ')[0]) locationScore = 10;
    else if (basicA.hometown === basicB.hometown) locationScore = 5;
    totalScore += locationScore;
    details.location = { score: locationScore, note: basicA.location === basicB.location ? '同城' : '异地' };
    
    // 学历匹配 15分
    const eduLevels = { 'phd': 5, 'master': 4, 'bachelor': 3, '大专': 2, 'high school': 1 };
    const eduDiff = Math.abs((eduLevels[basicA.education] || 0) - (eduLevels[basicB.education] || 0));
    const eduScore = eduDiff === 0 ? 15 : eduDiff === 1 ? 10 : eduDiff === 2 ? 5 : 0;
    totalScore += eduScore;
    details.education = { score: eduScore };
    
    // 收入匹配 15分
    let incomeScore = 0;
    if (basicA.income && basicB.income) {
      if (basicA.income === basicB.income) incomeScore = 15;
      else if (Math.abs(parseInt(basicA.income) - parseInt(basicB.income)) <= 5) incomeScore = 10;
      else incomeScore = 5;
    }
    totalScore += incomeScore;
    details.income = { score: incomeScore };
    
    // 兴趣爱好匹配 20分
    const hobbiesA = new Set(profileA.aboutMe.hobbies || []);
    const hobbiesB = new Set(profileB.aboutMe.hobbies || []);
    const commonHobbies = [...hobbiesA].filter(h => hobbiesB.has(h));
    const hobbyScore = Math.min(commonHobbies.length * 5, 20);
    totalScore += hobbyScore;
    details.hobbies = { score: hobbyScore, common: commonHobbies };
    
    return {
      total: totalScore,
      percentage: Math.round((totalScore / 100) * 100),
      details,
      level: totalScore >= 80 ? 'high度匹配' : totalScore >= 60 ? '比较匹配' : totalScore >= 40 ? '一般匹配' : '匹配度较low'
    };
  }

  /**
   * 脱敏处理
   */
  sanitizeProfile(profile) {
    return {
      userId: profile.userId,
      basicInfo: {
        nickname: profile.basicInfo.nickname,
        gender: profile.basicInfo.gender,
        age: profile.basicInfo.age,
        height: profile.basicInfo.height,
        location: profile.basicInfo.location.split(' ')[0] + ' *', // 只显示省市
        education: profile.basicInfo.education,
        occupation: profile.basicInfo.occupation,
        income: profile.basicInfo.income
      },
      aboutMe: profile.aboutMe,
      photos: profile.photos?.slice(0, 3) || []
    };
  }

  // ========== 沟通辅助 ==========

  /**
   * 生成开场白
   */
  generateOpener(myProfile, theirProfile, context = {}) {
    const openers = [];
    const commonHobbies = context.commonHobbies || [];
    
    // 基于共同兴趣
    if (commonHobbies.length > 0) {
      const hobby = commonHobbies[0];
      openers.push({
        type: 'hobby',
        content: `你好！看到你也喜欢${hobby}，最近有${this.getHobbyActivity(hobby)}吗？`,
        score: 90
      });
    }
    
    // 基于地域
    if (myProfile.basicInfo.location === theirProfile.basicInfo.location) {
      openers.push({
        type: 'location',
        content: `你好！我也在${theirProfile.basicInfo.location}，你平时周末一般去哪里玩？`,
        score: 80
      });
    }
    
    // 基于职业
    openers.push({
      type: 'occupation',
      content: `你好！看到你是做${theirProfile.basicInfo.occupation}的，平时工作忙吗？`,
      score: 70
    });
    
    // 通用开场
    openers.push({
      type: 'general',
      content: `你好！很high兴认识你，希望我们可以多了解一下彼此。`,
      score: 60
    });
    
    // 按评分排序
    openers.sort((a, b) => b.score - a.score);
    
    return {
      recommendations: openers.slice(0, 3),
      tips: [
        '真诚自然最重要',
        '避免过于套路的开场白',
        '根据对方回复灵活调整'
      ]
    };
  }

  getHobbyActivity(hobby) {
    const activities = {
      '旅游': '去哪里旅游',
      '摄影': '拍什么类型的照片',
      '读书': '读什么类型的书',
      '电影': '看什么类型的电影',
      '音乐': '听什么类型的音乐',
      '运动': '做什么运动',
      '美食': '尝试什么新餐厅',
      '游戏': '玩什么游戏'
    };
    return activities[hobby] || '什么有趣的活动';
  }

  /**
   * 推荐聊天话题
   */
  suggestTopics(myProfile, theirProfile, stage = 'initial') {
    const topics = {
      initial: [
        { topic: '工作/学习', questions: ['平时工作忙吗？', '工作medium最有成就感的事？'] },
        { topic: '兴趣爱好', questions: ['周末一般怎么安排？', '最近在看什么书/电影？'] },
        { topic: '生活日常', questions: ['平时喜欢吃什么？', '有养宠物吗？'] }
      ],
      middle: [
        { topic: '价值观', questions: ['对未来生活的期待？', '觉得两个人相处最重要的是什么？'] },
        { topic: '家庭', questions: ['家里有几口人？', '和父母关系怎么样？'] },
        { topic: '未来规划', questions: ['对未来几年的规划？', '理想medium的生活状态？'] }
      ],
      advanced: [
        { topic: '感情观', questions: ['之前为什么单身？', '理想medium的另一半是什么样的？'] },
        { topic: '生活习惯', questions: ['作息规律吗？', '有什么不能接受的点？'] },
        { topic: '经济观念', questions: ['对理财怎么看？', '消费观念是怎样的？'] }
      ]
    };
    
    return {
      stage,
      topics: topics[stage] || topics.initial,
      warnings: [
        '避免查户口式提问',
        '不要过度追问前任',
        '尊重对方隐私边界'
      ]
    };
  }

  // ========== 约会规划 ==========

  /**
   * Date Suggestions
   */
  suggestDateIdeas(location, preferences = {}) {
    const ideas = {
      first: [
        { type: 'coffee', name: '咖啡厅', pros: ['轻松氛围', '方便聊天', '随时可结束'], cons: ['可能太正式'] },
        { type: 'walk', name: '公园散步', pros: ['自然放松', '活动身体', '话题丰富'], cons: ['受天气影响'] },
        { type: 'bookstore', name: '书店/图书馆', pros: ['文艺氛围', '了解品味', '安静'], cons: ['不适合大声聊天'] }
      ],
      second: [
        { type: 'dinner', name: '特色餐厅', pros: ['正式一些', '了解口味', '时间较长'], cons: ['可能紧张'] },
        { type: 'activity', name: '手工/体验课', pros: ['有互动', '共同话题', '留下回忆'], cons: ['需要预约'] },
        { type: 'museum', name: '博物馆/展览', pros: ['有内涵', '话题多', '展示品味'], cons: ['可能无趣'] }
      ],
      advanced: [
        { type: 'outdoor', name: '户外活动', pros: ['亲近自然', '锻炼身体', '共同挑战'], cons: ['体力要求high'] },
        { type: 'cooking', name: '一起做饭', pros: ['生活气息', '协作互动', '温馨'], cons: ['需要场地'] },
        { type: 'travel', name: '短途旅行', pros: ['深入了解', '共同经历', '浪漫'], cons: ['时间成本high'] }
      ]
    };
    
    return {
      location,
      suggestions: ideas,
      tips: [
        '第一次约会选择公共场所',
        '提前确认对方喜好',
        '准备备选方案',
        '注意时间和节奏'
      ]
    };
  }

  // ========== 进展跟踪 ==========

  /**
   * Record Contact
   */
  recordContact(userId, targetId, contact) {
    const key = `${userId}_${targetId}`;
    
    if (!this.conversations[key]) {
      this.conversations[key] = {
        userId,
        targetId,
        startedAt: new Date().toISOString(),
        contacts: [],
        status: 'contacted'
      };
    }
    
    this.conversations[key].contacts.push({
      type: contact.type, // 'message', 'call', 'date'
      content: contact.content,
      timestamp: new Date().toISOString(),
      notes: contact.notes
    });
    
    this.conversations[key].lastContactAt = new Date().toISOString();
    this.saveConversations();
    
    return {
      success: true,
      conversation: this.conversations[key]
    };
  }

  /**
   * Get Contact History
   */
  getContactHistory(userId, targetId) {
    const key = `${userId}_${targetId}`;
    return this.conversations[key] || null;
  }

  /**
   * 更新状态
   */
  updateStatus(userId, targetId, status, note) {
    const key = `${userId}_${targetId}`;
    
    if (!this.conversations[key]) {
      return { success: false, error: '没有接触记录' };
    }
    
    this.conversations[key].status = status;
    this.conversations[key].statusNote = note;
    this.conversations[key].statusUpdatedAt = new Date().toISOString();
    
    this.saveConversations();
    
    return {
      success: true,
      status,
      message: `状态已更新为：${status}`
    };
  }

  // ========== Safety Reminders ==========

  getSafetyTips() {
    return {
      before: [
        '✅ 第一次见面选择公共场所',
        '✅ 告知朋友或家人约会信息',
        '✅ 保持手机电量充足',
        '✅ 不要透露详细住址'
      ],
      during: [
        '✅ 注意饮品安全，不要离开视线',
        '✅ 保持清醒，适量饮酒',
        '✅ 信任直觉，不舒服就离开',
        '✅ 不要轻易跟随去私密场所'
      ],
      redFlags: [
        '🚩 急于确定关系',
        '🚩 频繁借钱或要求投资',
        '🚩 拒绝视频或见面',
        '🚩 信息前后矛盾',
        '🚩 过度打探隐私',
        '🚩 情绪不稳定或控制欲强'
      ],
      scams: [
        '💰 杀猪盘：培养感情后诱导投资',
        '💰 裸聊诈骗：诱导视频后勒索',
        '💰 借贷诈骗：以各种理由借钱',
        '💰 传销拉人：诱导加入组织'
      ]
    };
  }
}

module.exports = { BlindDateAssistant };
