const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { Xiangqin } = require('./scripts/index');

const dataDir = path.join(os.homedir(), '.openclaw', 'skills-data', 'xiangqin');
const testUsers = ['test_male', 'test_female'];

function cleanup() {
  for (const file of ['profiles.json', 'matches.json', 'conversations.json']) {
    const full = path.join(dataDir, file);
    if (fs.existsSync(full)) fs.unlinkSync(full);
  }
}

function run() {
  cleanup();

  const app = new Xiangqin();

  const male = app.createProfile('test_male', {
    nickname: '阿哲',
    gender: '男',
    birthYear: 1995,
    height: 178,
    location: '北京 海淀',
    hometown: '河北',
    education: '本科',
    occupation: '工程师',
    income: '20',
    hobbies: ['旅游', '电影', '读书'],
    selfDescription: '认真生活，也认真找对象，希望找到合适的人。',
    values: '真诚'
  });

  const female = app.createProfile('test_female', {
    nickname: '小雨',
    gender: '女',
    birthYear: 1997,
    height: 165,
    location: '北京 朝阳',
    hometown: '河北',
    education: '本科',
    occupation: '产品经理',
    income: '18',
    hobbies: ['旅游', '电影', '美食'],
    selfDescription: '希望认识稳定、善良、有责任感的人。',
    values: '靠谱'
  });

  assert.equal(male.success, true, 'male profile should be created');
  assert.equal(female.success, true, 'female profile should be created');
  assert.equal(male.profile.preferences.ageRange.min, 26, 'default ageRange min should be age-based');
  assert.equal(male.profile.preferences.ageRange.max, 34, 'default ageRange max should be age-based');

  const loaded = app.getProfile('test_male');
  assert.equal(loaded.basicInfo.nickname, '阿哲', 'profile lookup should work');

  const matches = app.findMatches('test_male', { limit: 5 });
  assert.equal(matches.success, true, 'matching should succeed');
  assert.equal(matches.matches.length, 1, 'should find one compatible profile');
  assert.equal(matches.matches[0].profile.basicInfo.nickname, '小雨', 'matched profile should be 小雨');

  const opener = app.generateOpener(app.getProfile('test_male'), app.getProfile('test_female'), {
    commonHobbies: ['旅游', '电影']
  });
  assert.ok(opener.recommendations.length > 0, 'should generate opener recommendations');

  const record = app.recordContact('test_male', 'test_female', {
    type: 'message',
    content: '你好，很高兴认识你。'
  });
  assert.equal(record.success, true, 'contact record should be saved');

  const history = app.getContactHistory('test_male', 'test_female');
  assert.equal(history.contacts.length, 1, 'contact history should contain one record');

  const safety = app.getSafetyTips();
  assert.ok(Array.isArray(safety.redFlags) && safety.redFlags.length > 0, 'safety tips should exist');

  console.log('All tests passed for xiangqin skill.');
}

run();
