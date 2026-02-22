# frozen_string_literal: true

module Blackroad
  # API for managing tasks
  class TaskAPI
    def initialize(client)
      @client = client
    end

    # Dispatch a new task
    #
    # @param title [String] Task title
    # @param description [String] Task description
    # @param priority [String] Priority (low, medium, high, urgent)
    # @param division [String] Target division
    # @param target_level [Integer] Target agent level
    # @param metadata [Hash] Additional metadata
    # @return [Hash] Created task
    def dispatch(title:, description: nil, priority: "medium", division: nil, target_level: nil, metadata: nil)
      body = { title: title, priority: priority }
      body[:description] = description if description
      body[:division] = division if division
      body[:target_level] = target_level if target_level
      body[:metadata] = metadata if metadata

      @client.post("/tasks", body)
    end

    # Get a specific task by ID
    #
    # @param task_id [String] The task ID
    # @return [Hash] Task data
    def get(task_id)
      @client.get("/tasks/#{task_id}")
    end

    # List tasks with optional filters
    #
    # @param status [String] Filter by status
    # @param priority [String] Filter by priority
    # @param division [String] Filter by division
    # @param limit [Integer] Maximum results
    # @param offset [Integer] Offset for pagination
    # @return [Array<Hash>] List of tasks
    def list(status: nil, priority: nil, division: nil, limit: nil, offset: nil)
      params = {}
      params[:status] = status if status
      params[:priority] = priority if priority
      params[:division] = division if division
      params[:limit] = limit if limit
      params[:offset] = offset if offset

      response = @client.get("/tasks", params)
      response["tasks"] || []
    end

    # Complete a task
    #
    # @param task_id [String] The task ID
    # @param result [String] Completion result/notes
    # @return [Hash] Updated task
    def complete(task_id, result: nil)
      body = { status: "completed" }
      body[:result] = result if result
      @client.put("/tasks/#{task_id}", body)
    end

    # Fail a task
    #
    # @param task_id [String] The task ID
    # @param reason [String] Failure reason
    # @return [Hash] Updated task
    def fail(task_id, reason: nil)
      body = { status: "failed" }
      body[:result] = reason if reason
      @client.put("/tasks/#{task_id}", body)
    end

    # Assign a task to an agent
    #
    # @param task_id [String] The task ID
    # @param agent_id [String] The agent ID
    # @return [Hash] Updated task
    def assign(task_id, agent_id)
      @client.put("/tasks/#{task_id}", { assigned_agent: agent_id, status: "assigned" })
    end

    # Cancel a task
    #
    # @param task_id [String] The task ID
    # @return [Hash] Response
    def cancel(task_id)
      @client.delete("/tasks/#{task_id}")
    end

    # Get task statistics
    #
    # @return [Hash] Statistics
    def stats
      @client.get("/tasks/stats")
    end

    # Get pending tasks
    #
    # @return [Array<Hash>] List of pending tasks
    def pending
      list(status: "pending")
    end

    # Get in-progress tasks
    #
    # @return [Array<Hash>] List of in-progress tasks
    def in_progress
      list(status: "in_progress")
    end

    # Get tasks by division
    #
    # @param division [String] Division name
    # @return [Array<Hash>] List of tasks
    def by_division(division)
      list(division: division)
    end

    # Get urgent tasks
    #
    # @return [Array<Hash>] List of urgent tasks
    def urgent
      list(priority: "urgent")
    end
  end
end
