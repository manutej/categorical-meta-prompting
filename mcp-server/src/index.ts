#!/usr/bin/env node

/**
 * Categorical Meta-Prompting MCP Server
 *
 * Implements functorial data migration for meta-prompting:
 * - analyze_complexity: Task complexity analysis via Δ, Σ functors
 * - iterate_prompt: Quality-driven iteration (future)
 *
 * Based on Spivak's functorial data migration framework
 */

import { Server } from '@modelcontext/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontext/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontext/sdk/types.js';
import { analyzeComplexity, ComplexityInput } from './tools/analyze-complexity.js';

const server = new Server(
  {
    name: 'categorical-meta-prompting',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * List available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'analyze_complexity',
        description:
          'Analyze task complexity and recommend meta-prompting tier (L1-L7) using categorical complexity schema',
        inputSchema: {
          type: 'object',
          properties: {
            task: {
              type: 'string',
              description: 'The task description to analyze',
            },
          },
          required: ['task'],
        },
      },
    ],
  };
});

/**
 * Handle tool calls
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'analyze_complexity') {
      const input = args as ComplexityInput;
      const result = await analyzeComplexity(input);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${errorMessage}`,
        },
      ],
      isError: true,
    };
  }
});

/**
 * Start server
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Categorical Meta-Prompting MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
