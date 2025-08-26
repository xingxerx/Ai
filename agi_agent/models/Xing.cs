/**
 * Connect model with mcp tools in .NET 10
 * # Run this script
 * > dotnet run <this-script-path>.cs
 */

#:package OpenAI@*-*
#:package ModelContextProtocol@*-*
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;
using System.Threading.Tasks;
using OpenAI;
using OpenAI.Chat;
using ModelContextProtocol;
using ModelContextProtocol.Client;

// Main execution
var client = new MCPClient();
var messages = new List<ChatMessage>
{
    ChatMessage.CreateSystemMessage("Build me a modular AGI agent with the following architecture:\n\n1. **Reasoning Engine** for problem decomposition, strategy selection, causal inference, and decision-making under uncertainty.  \n2. **Task Planning System** that breaks complex tasks into steps with dependency analysis, resource allocation, and adaptive optimization.  \n3. **Knowledge Management System** including factual, procedural, episodic, and semantic knowledge, stored in a knowledge graph with retrieval and update mechanisms.  \n4. **Tool Integration Framework** to dynamically discover, register, and call external APIs, web services, file systems, and tools, with error handling and result interpretation.  \n5. **Learning and Adaptation System** with reinforcement learning, pattern recognition, knowledge acquisition, and meta-learning capabilities.  \n6. **Safety and Control System** enforcing constraints, risk assessment, action approval workflows, rollback, and human-in-the-loop oversight.  \n7. **Communication Interface** with natural language processing, multi-modal support, progress reporting, clarification requests, and results presentation.  \n\n**System Principles**: modular, extensible, safe-first, transparent, adaptive, human-supervised.  \n\n**System Architecture**:  \n- User Interface Layer  \n- Communication Interface  \n- Core: Reasoning Engine, Task Planner, Safety Controller  \n- Supporting: Knowledge Management, Learning System  \n- Tool Integration Framework  \n- External APIs, File System, Web Services, Tools  \n\n**Tech stack considerations**:  \n- Backend: Python, Rust, Go, or TypeScript  \n- AI/ML: LLMs, reinforcement learning, vector DBs, neural-symbolic reasoning  \n- Storage: Graph DBs, vector stores, SQL/NoSQL, file systems  \n\n**Next steps**:  \n1. Select backend stack  \n2. Implement reasoning engine  \n3. Build task planner  \n4. Integrate tool framework  \n5. Add safety mechanisms  \n6. Develop UI  \n7. Implement adaptive learning  \n8. Add full testing  \n\n**Success metrics**: high task completion, low incident rate, strong adaptability, fast response time, efficient resource use, high user satisfaction.  \n\nDeliver this as a modular system blueprint with working code stubs for each component, ready for incremental implementation.\n"),
    ChatMessage.CreateUserMessage(
        "You are an AGI-style agent.  \nYour architecture must include:  \n- Reasoning Engine for problem decomposition, causal inference, and decision-making under uncertainty.  \n- Task Planning System for breaking down tasks, dependency analysis, and adaptive optimization.  \n- Knowledge Management with factual, procedural, episodic, and semantic memory stored in a knowledge graph.  \n- Tool Integration Framework to dynamically call APIs, web services, file systems, and external tools.  \n- Learning and Adaptation System with reinforcement learning, pattern recognition, and meta-learning.  \n- Safety and Control System with constraint enforcement, rollback, and human-in-the-loop approvals.  \n- Communication Interface with natural language, multimodal support, progress updates, and results presentation.  \n\nPrinciples: modular, extensible, safe-first, transparent, adaptive, human-supervised.  \nSuccess metrics: task completion, low safety incidents, adaptability, response speed, resource efficiency, and user satisfaction.  \n\nBehave as a **general-purpose agent** that can plan, reason, learn, and act safely across domains. Provide clear step-by-step reasoning, request clarifications when needed, and show transparent decision trails."
    ),
};

try
{
    await client.ConnectStdioServerAsync(
        "mcp-mesp3ugj", 
        "npx", 
        new[]
        {
            "-y",
            "@playwright/mcp@latest",
        },
        new Dictionary<string, string>
        {
        }
    );
    await client.ChatWithToolsAsync(messages);
}
catch (Exception ex)
{
    Console.WriteLine($"\nError: {ex.Message}");
}
finally
{
    client.Dispose();
    await Task.Delay(1000);
}

public class MCPClient
{
    private readonly Dictionary<string, ServerInfo> _servers = new();
    private readonly Dictionary<string, string> _toolToServerMap = new();
    private readonly ChatClient _openAI;
    private readonly JsonSerializerOptions _jsonOptions = new()
    {
        TypeInfoResolver = new DefaultJsonTypeInfoResolver()
    };

    public class ServerInfo
    {
        public IMcpClient? Client { get; set; }
        public List<McpClientTool> Tools { get; set; } = new();
    }

    public MCPClient()
    {
        // To authenticate with the model you will need to generate a github gho token in your GitHub settings.
        // Create your github gho token by following instructions here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
        var apiKey = Environment.GetEnvironmentVariable("GITHUB_TOKEN");
        var credential = new System.ClientModel.ApiKeyCredential(apiKey);
        var client = new OpenAIClient(credential, new OpenAIClientOptions
        {
            Endpoint = new Uri("https://models.github.ai/inference")
        });
        _openAI = client.GetChatClient("openai/gpt-4o");
    }

    /// <summary>
    /// Connect to an MCP server using STDIO transport
    /// </summary>
    /// <param name="serverId">Unique identifier for this server connection</param>
    /// <param name="command">Command to run the MCP server</param>
    /// <param name="args">Arguments for the command</param>
    /// <param name="env">Optional environment variables</param>
    public async Task ConnectStdioServerAsync(string serverId, string command, string[] args, Dictionary<string, string>? env = null)
    {
        var transportOptions = new StdioClientTransportOptions
        {
            Name = serverId,
            Command = command,
            Arguments = args
        };

        var transport = new StdioClientTransport(transportOptions);
        var client = await McpClientFactory.CreateAsync(transport);
        
        await RegisterServerAsync(serverId, client);
    }

    /// <summary>
    /// Connect to an MCP server using SSE transport
    /// </summary>
    /// <param name="serverId">Unique identifier for this server connection</param>
    /// <param name="url">URL of the SSE server</param>
    /// <param name="headers">Optional HTTP headers</param>
    public async Task ConnectSseServerAsync(string serverId, string url, Dictionary<string, string>? headers = null)
    {
        var transportOptions = new SseClientTransportOptions
        {
            Endpoint = new Uri(url)
        };

        var transport = new SseClientTransport(transportOptions);
        var client = await McpClientFactory.CreateAsync(transport);
        
        await RegisterServerAsync(serverId, client);
    }

    private async Task RegisterServerAsync(string serverId, IMcpClient client)
    {
        var tools = await client.ListToolsAsync();
        
        _servers[serverId] = new ServerInfo
        {
            Client = client,
            Tools = tools.ToList()
        };

        // Update tool-to-server mapping
        foreach (var tool in tools)
        {
            _toolToServerMap[tool.Name] = serverId;
        }

        Console.WriteLine($"\nConnected to server '{serverId}' with tools: {string.Join(", ", tools.Select(t => t.Name))}");
    }

    /// <summary>
    /// Chat with model using MCP tools
    /// </summary>
    /// <param name="messages">Messages to send to the model</param>
    public async Task ChatWithToolsAsync(List<ChatMessage> messages)
    {
        if (_servers.Count == 0)
        {
            throw new InvalidOperationException("No MCP servers connected. Connect to at least one server first.");
        }

        // Collect tools from all connected servers
        var availableTools = new List<ChatTool>();
        foreach (var (serverId, serverInfo) in _servers)
        {
            foreach (var tool in serverInfo.Tools)
            {
                availableTools.Add(ChatTool.CreateFunctionTool(
                    functionName: tool.Name,
                    functionDescription: tool.Description,
                    functionParameters: BinaryData.FromString("{}")
                ));
            }
        }

        while (true)
        {
            var options = new ChatCompletionOptions
            {
                Tools = { },
                Temperature = 1f,
                TopP = 1f,
            };

            foreach (var tool in availableTools)
            {
                options.Tools.Add(tool);
            }

            var response = await _openAI.CompleteChatAsync(messages, options);
            bool hasToolCall = false;

            if (response.Value.ToolCalls?.Count > 0)
            {
                hasToolCall = true;
                // Add assistant message with tool calls only once
                messages.Add(ChatMessage.CreateAssistantMessage(response.Value.ToolCalls));

                foreach (var toolCall in response.Value.ToolCalls)
                {
                    var toolName = toolCall.FunctionName;
                    var toolArgs = JsonSerializer.Deserialize<Dictionary<string, object>>(toolCall.FunctionArguments, _jsonOptions);

                    // Find the appropriate server for this tool
                    if (_toolToServerMap.TryGetValue(toolName, out var serverId))
                    {
                        var serverInfo = _servers[serverId];
                        var serverClient = serverInfo.Client;
                        
                        if (serverClient != null)
                        {
                            // Execute tool call on the appropriate server
                            var readOnlyArgs = toolArgs?.ToDictionary(kvp => kvp.Key, kvp => (object?)kvp.Value) as IReadOnlyDictionary<string, object?>;
                            var callResult = await serverClient.CallToolAsync(toolName, readOnlyArgs);

                            var resultContent = string.Join("\n", callResult.Content
                                .Where(c => c.Type == "text")
                                .Select(c => c is ModelContextProtocol.Protocol.TextContentBlock textBlock ? textBlock.Text : c.ToString()));
                            Console.WriteLine($"[Server '{serverId}' call tool '{toolName}' with args {JsonSerializer.Serialize(toolArgs, _jsonOptions)}]: {resultContent}");

                            messages.Add(ChatMessage.CreateToolMessage(toolCall.Id, resultContent));
                        }
                    }
                }
            }
            else
            {
                messages.Add(ChatMessage.CreateAssistantMessage(response.Value.Content[0].Text));
                Console.WriteLine($"[Model Response]: {response.Value.Content[0].Text}");
            }

            if (!hasToolCall)
            {
                break;
            }
        }
    }

    public void Dispose()
    {
        foreach (var (serverId, serverInfo) in _servers)
        {
            try
            {
                if (serverInfo.Client is IDisposable disposable)
                {
                    disposable.Dispose();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error disposing server '{serverId}': {ex.Message}");
            }
        }
    }
}