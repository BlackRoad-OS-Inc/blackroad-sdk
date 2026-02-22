# frozen_string_literal: true

module Blackroad
  # API for memory operations
  class MemoryAPI
    def initialize(client)
      @client = client
    end

    # Log a new memory entry
    #
    # @param action [String] Action type
    # @param entity [String] Entity name
    # @param details [String] Details
    # @param tags [Array<String>] Tags
    # @param metadata [Hash] Additional metadata
    # @return [Hash] Created entry
    def log(action:, entity:, details: nil, tags: nil, metadata: nil)
      body = { action: action, entity: entity }
      body[:details] = details if details
      body[:tags] = tags if tags
      body[:metadata] = metadata if metadata

      @client.post("/memory", body)
    end

    # Query memory entries
    #
    # @param search [String] Search query
    # @param action [String] Filter by action
    # @param entity [String] Filter by entity
    # @param tags [Array<String>] Filter by tags
    # @param since [Time] Entries since this time
    # @param until_time [Time] Entries until this time
    # @param limit [Integer] Maximum results
    # @param offset [Integer] Offset for pagination
    # @return [Array<Hash>] List of entries
    def query(search: nil, action: nil, entity: nil, tags: nil, since: nil, until_time: nil, limit: 100, offset: nil)
      params = { limit: limit }
      params[:q] = search if search
      params[:action] = action if action
      params[:entity] = entity if entity
      params[:tags] = tags.join(",") if tags
      params[:since] = since.iso8601 if since
      params[:until] = until_time.iso8601 if until_time
      params[:offset] = offset if offset

      response = @client.get("/memory", params)
      response["entries"] || []
    end

    # Get a specific entry by hash
    #
    # @param entry_hash [String] Entry hash
    # @return [Hash] Entry data
    def get(entry_hash)
      @client.get("/memory/#{entry_hash}")
    end

    # Get recent entries
    #
    # @param limit [Integer] Maximum results
    # @return [Array<Hash>] List of entries
    def recent(limit = 50)
      query(limit: limit)
    end

    # Get agent state
    #
    # @param agent_id [String] Agent ID
    # @return [Hash] Agent state
    def agent_state(agent_id)
      @client.get("/memory/agents/#{agent_id}/state")
    end

    # Sync agent state
    #
    # @param agent_id [String] Agent ID
    # @param state [Hash] State to sync
    # @return [Hash] Response
    def sync_state(agent_id, state)
      @client.post("/memory/agents/#{agent_id}/state", state)
    end

    # Broadcast a message
    #
    # @param type [String] Message type
    # @param payload [String] Message payload
    # @return [Hash] Response with broadcast_id
    def broadcast(type, payload)
      @client.post("/memory/broadcast", { type: type, payload: payload })
    end

    # Share a TIL (Today I Learned)
    #
    # @param category [String] Category
    # @param learning [String] What was learned
    # @return [Hash] Created entry
    def til(category, learning)
      log(
        action: "til",
        entity: category,
        details: learning,
        tags: ["til", category]
      )
    end

    # Get memory statistics
    #
    # @return [Hash] Statistics
    def stats
      @client.get("/memory/stats")
    end

    # Verify hash chain integrity
    #
    # @param start_hash [String] Starting hash (optional)
    # @return [Hash] Verification result
    def verify_chain(start_hash: nil)
      params = {}
      params[:start] = start_hash if start_hash
      @client.get("/memory/verify", params)
    end
  end
end
