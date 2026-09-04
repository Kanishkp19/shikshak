#!/usr/bin/env node
/**
 * Engineering Coordination System (ECC) - Prompt Middleware Gateway
 *
 * This script runs as an Antigravity lifecycle hook (PreInvocation, PreToolUse, PostInvocation)
 * ensuring that every user prompt passes through the ECC coordination pipeline.
 */

const fs = require('fs');
const path = require('path');

const hookEvent = process.argv[2] || 'pre-invocation';

let inputData = '';
process.stdin.setEncoding('utf8');

process.stdin.on('data', chunk => {
  inputData += chunk;
});

process.stdin.on('end', () => {
  let payload = {};
  try {
    if (inputData.trim()) {
      payload = JSON.parse(inputData);
    }
  } catch (err) {
    // If input is not JSON, proceed with empty payload
  }

  switch (hookEvent) {
    case 'pre-invocation': {
      // Injected ephemeral message before the model generates output
      const response = {
        injectSteps: [
          {
            ephemeralMessage: `[ECC Middleware Gateway Active]
Every prompt MUST be processed through the Engineering Coordination System:
1. CLASSIFY INTENT: Determine domain (Architecture, Feature, Bug, Security, Database, UI/Web, Refactor, Build).
2. DISPATCH SUBAGENT: Bind to the specialized agent (planner, architect, tdd-guide, code-reviewer, security-reviewer, build-error-resolver, typescript-reviewer, python-reviewer, database-reviewer).
3. ENFORCE WORKFLOWS: Ground via search-first/graphify; apply tdd-workflow; maintain immutability & validation.
4. GATE QUALITY: Run security-reviewer and code-reviewer before marking complete.
Always begin response with: [ECC Dispatch: <Subagent> | Active Workflows: <skills/rules>]`
          }
        ]
      };
      process.stdout.write(JSON.stringify(response));
      break;
    }

    case 'pre-tool-use': {
      // Validate tool execution against ECC safety guardrails
      const toolCall = payload.toolCall || {};
      const toolName = toolCall.name || '';
      const args = toolCall.args || {};

      // Detect potentially dangerous shell commands
      if (toolName === 'run_command') {
        const cmd = (args.CommandLine || '').trim();
        if (/rm\s+-rf\s+(\/|~|\$HOME|\.\.)($|\s)/.test(cmd)) {
          process.stdout.write(JSON.stringify({
            decision: 'deny',
            reason: '[ECC Security Gate] Dangerous recursive deletion blocked.'
          }));
          return;
        }
      }

      process.stdout.write(JSON.stringify({ decision: 'allow' }));
      break;
    }

    case 'post-tool-use': {
      process.stdout.write(JSON.stringify({}));
      break;
    }

    case 'stop': {
      process.stdout.write(JSON.stringify({ decision: 'allow' }));
      break;
    }

    default: {
      process.stdout.write(JSON.stringify({}));
      break;
    }
  }
});
