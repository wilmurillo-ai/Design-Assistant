#!/usr/bin/env node
/**
 * Blind Date Assistant CLI
 */

const { BlindDateAssistant } = require('./index');

const app = new BlindDateAssistant();

function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const userId = args[1] || 'user_default';

  try {
    switch (command) {
      case 'profile': {
        const action = args[2];
        if (action === 'create') {
          const info = JSON.parse(args[3] || '{}');
          const result = app.createProfile(userId, info);
          console.log(JSON.stringify(result, null, 2));
        } else {
          const profile = app.getProfile(userId);
          if (profile) {
            console.log('=== My Profile ===');
            console.log(`Nickname: ${profile.basicInfo.nickname}`);
            console.log(`Gender: ${profile.basicInfo.gender}`);
            console.log(`Age: ${profile.basicInfo.age}`);
            console.log(`Height: ${profile.basicInfo.height}cm`);
            console.log(`Education: ${profile.basicInfo.education}`);
            console.log(`Occupation: ${profile.basicInfo.occupation}`);
            console.log(`Income: ${profile.basicInfo.income}`);
            console.log(`Location: ${profile.basicInfo.location}`);
            console.log(`\nProfile Completeness: ${app.calculateCompleteness(profile).percentage}%`);
          } else {
            console.log('Profile not created yet');
          }
        }
        break;
      }

      case 'match': {
        const limit = parseInt(args[2]) || 5;
        const result = app.findMatches(userId, { limit });
        if (result.success) {
          console.log(`=== Recommended Matches (${result.total}) ===\n`);
          result.matches.forEach((m, i) => {
            console.log(`${i + 1}. ${m.profile.basicInfo.nickname}`);
            console.log(`   ${m.profile.basicInfo.age} years | ${m.profile.basicInfo.height}cm | ${m.profile.basicInfo.education}`);
            console.log(`   ${m.profile.basicInfo.occupation} | ${m.profile.basicInfo.location}`);
            console.log(`   Match Score: ${m.matchScore.percentage}% - ${m.matchScore.level}`);
            if (m.matchScore.details.hobbies.common?.length > 0) {
              console.log(`   Common Hobbies: ${m.matchScore.details.hobbies.common.join(', ')}`);
            }
            console.log();
          });
        } else {
          console.log(result.error);
        }
        break;
      }

      case 'opener': {
        const targetId = args[2];
        if (!targetId) {
          console.log('Usage: blind-date-assistant opener <targetID>');
          process.exit(1);
        }
        const myProfile = app.getProfile(userId);
        const theirProfile = app.getProfile(targetId);
        if (!myProfile || !theirProfile) {
          console.log('Profile incomplete');
          process.exit(1);
        }
        const result = app.generateOpener(myProfile, theirProfile, {
          commonHobbies: ['travel', 'movies']
        });
        console.log('=== Recommended Openers ===\n');
        result.recommendations.forEach((r, i) => {
          console.log(`${i + 1}. [${r.type}] ${r.content}`);
        });
        console.log('\n💡 Tips:');
        result.tips.forEach(t => console.log(`   ${t}`));
        break;
      }

      case 'topics': {
        const stage = args[2] || 'initial';
        const result = app.suggestTopics(null, null, stage);
        console.log(`=== ${stage === 'initial' ? 'Initial' : stage === 'middle' ? 'Deep' : 'Advanced'} Topics ===\n`);
        result.topics.forEach(t => {
          console.log(`📌 ${t.topic}`);
          t.questions.forEach(q => console.log(`   • ${q}`));
          console.log();
        });
        break;
      }

      case 'date': {
        const location = args[2] || 'Beijing';
        const result = app.suggestDateIdeas(location);
        console.log(`=== ${location} Date Suggestions ===\n`);
        for (const [stage, ideas] of Object.entries(result.suggestions)) {
          console.log(`\n【${stage === 'first' ? 'First' : stage === 'second' ? 'Second' : 'Advanced'} Date】`);
          ideas.forEach(idea => {
            console.log(`  ${idea.name}`);
            console.log(`    Pros: ${idea.pros.join(', ')}`);
            console.log(`    Cons: ${idea.cons.join(', ')}`);
          });
        }
        break;
      }

      case 'contact': {
        const targetId = args[2];
        const content = args.slice(3).join(' ');
        if (!targetId || !content) {
          console.log('Usage: blind-date-assistant contact <userID> <targetID> <content>');
          process.exit(1);
        }
        const result = app.recordContact(userId, targetId, {
          type: 'message',
          content
        });
        console.log('Contact record saved');
        break;
      }

      case 'history': {
        const targetId = args[2];
        if (!targetId) {
          console.log('Usage: blind-date-assistant history <userID> <targetID>');
          process.exit(1);
        }
        const history = app.getContactHistory(userId, targetId);
        if (history) {
          console.log(`=== Contact History ===`);
          console.log(`Status: ${history.status}`);
          console.log(`Started: ${history.startedAt}`);
          console.log(`Contacts: ${history.contacts.length}`);
          history.contacts.forEach((c, i) => {
            console.log(`\n${i + 1}. [${c.type}] ${c.timestamp}`);
            console.log(`   ${c.content}`);
          });
        } else {
          console.log('No contact records yet');
        }
        break;
      }

      case 'safety': {
        const tips = app.getSafetyTips();
        console.log('=== Safety Reminders ===\n');
        console.log('【Before Meeting】');
        tips.before.forEach(t => console.log(`  ${t}`));
        console.log('\n【During Meeting】');
        tips.during.forEach(t => console.log(`  ${t}`));
        console.log('\n【Red Flags】');
        tips.redFlags.forEach(t => console.log(`  ${t}`));
        console.log('\n【Common Scams】');
        tips.scams.forEach(t => console.log(`  ${t}`));
        break;
      }

      default:
        console.log(`
Blind Date Assistant

Usage:
  blind-date-assistant profile <userID> [create <profileJSON>]    View/Create profile
  blind-date-assistant match <userID> [count]                    Find matches
  blind-date-assistant opener <userID> <targetID>                Generate opener
  blind-date-assistant topics [initial/middle/advanced]          Suggest topics
  blind-date-assistant date [city]                               Date suggestions
  blind-date-assistant contact <userID> <targetID> <content>     Record contact
  blind-date-assistant history <userID> <targetID>               View history
  blind-date-assistant safety                                    Safety reminders

Examples:
  blind-date-assistant profile user1 create '{"nickname":"Tom","gender":"male","birthYear":1995,"height":175,"location":"Beijing","education":"bachelor","occupation":"developer","hobbies":["travel","movies"]}'
  blind-date-assistant match user1 10
  blind-date-assistant opener user1 user2
        `);
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
