# frozen_string_literal: true

module Blackroad
  # API for managing agents
  class AgentAPI
    def initialize(client)
      @client = client
    end

    # List agents with optional filters
    #
    # @param type [String] Filter by agent type
    # @param division [String] Filter by division
    # @param level [Integer] Filter by level
    # @param status [String] Filter by status
    # @param limit [Integer] Maximum results
    # @param offset [Integer] Offset for pagination
    # @return [Array<Hash>] List of agents
    def list(type: nil, division: nil, level: nil, status: nil, limit: nil, offset: nil)
      params = {}
      params[:type] = type if type
      params[:division] = division if division
      params[:level] = level if level
      params[:status] = status if status
      params[:limit] = limit if limit
      params[:offset] = offset if offset

      response = @client.get("/agents", params)
      response["agents"] || []
    end

    # Get a specific agent by ID
    #
    # @param agent_id [String] The agent ID
    # @return [Hash] Agent data
    def get(agent_id)
      @client.get("/agents/#{agent_id}")
    end

    # Register a new agent
    #
    # @param name [String] Agent name
    # @param type [String] Agent type (default: "ai")
    # @param division [String] Division name
    # @param level [Integer] Agent level (default: 4)
    # @param metadata [Hash] Additional metadata
    # @return [Hash] Created agent
    def register(name:, type: "ai", division: nil, level: 4, metadata: nil)
      body = { name: name, type: type, level: level }
      body[:division] = division if division
      body[:metadata] = metadata if metadata

      @client.post("/agents", body)
    end

    # Send a heartbeat for an agent
    #
    # @param agent_id [String] The agent ID
    # @param load [Float] Current load (0.0 to 1.0)
    # @return [Hash] Response
    def heartbeat(agent_id, load: nil)
      body = {}
      body[:load] = load if load
      @client.post("/agents/#{agent_id}/heartbeat", body)
    end

    # Update agent status
    #
    # @param agent_id [String] The agent ID
    # @param status [String] New status
    # @return [Hash] Updated agent
    def update_status(agent_id, status)
      @client.put("/agents/#{agent_id}", { status: status })
    end

    # Delete an agent
    #
    # @param agent_id [String] The agent ID
    # @return [Hash] Response
    def delete(agent_id)
      @client.delete("/agents/#{agent_id}")
    end

    # Get agent statistics
    #
    # @return [Hash] Statistics
    def stats
      @client.get("/agents/stats")
    end

    # Get agents by division
    #
    # @param division [String] Division name
    # @return [Array<Hash>] List of agents
    def by_division(division)
      list(division: division)
    end

    # Get Level 2 commanders
    #
    # @return [Array<Hash>] List of commander agents
    def commanders
      list(level: 2)
    end

    # Get Level 3 managers
    #
    # @return [Array<Hash>] List of manager agents
    def managers
      list(level: 3)
    end

    # Get Level 4 workers
    #
    # @return [Array<Hash>] List of worker agents
    def workers
      list(level: 4)
    end
  end
end
