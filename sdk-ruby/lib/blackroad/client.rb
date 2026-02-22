# frozen_string_literal: true

require "faraday"
require "faraday/retry"
require "json"

module Blackroad
  # Main client for the BlackRoad API
  class Client
    DEFAULT_BASE_URL = "https://api.blackroad.io/v1"
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3

    attr_reader :agents, :tasks, :memory

    # Initialize a new BlackRoad client
    #
    # @param api_key [String] API key (defaults to BLACKROAD_API_KEY env var)
    # @param base_url [String] Base URL for API (defaults to https://api.blackroad.io/v1)
    # @param timeout [Integer] Request timeout in seconds (defaults to 30)
    # @param max_retries [Integer] Max retry attempts (defaults to 3)
    #
    # @example
    #   client = Blackroad::Client.new(api_key: "your-api-key")
    #   agents = client.agents.list
    #
    def initialize(api_key: nil, base_url: nil, timeout: nil, max_retries: nil)
      @api_key = api_key || ENV["BLACKROAD_API_KEY"]
      raise AuthenticationError, "API key required. Set BLACKROAD_API_KEY environment variable or pass api_key." unless @api_key

      @base_url = (base_url || ENV["BLACKROAD_API_URL"] || DEFAULT_BASE_URL).chomp("/")
      @timeout = timeout || DEFAULT_TIMEOUT
      @max_retries = max_retries || DEFAULT_MAX_RETRIES

      @connection = build_connection

      # Initialize API modules
      @agents = AgentAPI.new(self)
      @tasks = TaskAPI.new(self)
      @memory = MemoryAPI.new(self)
    end

    # Make a GET request
    def get(endpoint, params = {})
      request(:get, endpoint, params: params)
    end

    # Make a POST request
    def post(endpoint, body = {})
      request(:post, endpoint, body: body)
    end

    # Make a PUT request
    def put(endpoint, body = {})
      request(:put, endpoint, body: body)
    end

    # Make a DELETE request
    def delete(endpoint)
      request(:delete, endpoint)
    end

    # Check API health
    #
    # @return [Hash] Health status
    def health
      get("/health")
    end

    # Get API version
    #
    # @return [String] Version string
    def version
      get("/version")["version"]
    end

    private

    def build_connection
      Faraday.new(url: @base_url) do |conn|
        conn.request :retry, max: @max_retries, interval: 1, backoff_factor: 2,
                             retry_statuses: [429, 500, 502, 503, 504]
        conn.options.timeout = @timeout
        conn.headers["Authorization"] = "Bearer #{@api_key}"
        conn.headers["Content-Type"] = "application/json"
        conn.headers["User-Agent"] = "blackroad-ruby/#{VERSION}"
      end
    end

    def request(method, endpoint, params: nil, body: nil)
      path = endpoint.start_with?("/") ? endpoint : "/#{endpoint}"

      response = @connection.send(method) do |req|
        req.url path
        req.params = params if params && !params.empty?
        req.body = body.to_json if body
      end

      handle_response(response, endpoint)
    rescue Faraday::ConnectionFailed, Faraday::TimeoutError => e
      raise ConnectionError.new("Connection failed: #{e.message}", cause: e)
    end

    def handle_response(response, endpoint)
      return JSON.parse(response.body) if response.success?

      case response.status
      when 401
        raise AuthenticationError
      when 404
        raise NotFoundError, endpoint
      when 422
        raise ValidationError, response.body
      when 429
        retry_after = response.headers["Retry-After"]&.to_i || 1
        raise RateLimitError, retry_after
      else
        raise Error.new("API error (#{response.status}): #{response.body}", status_code: response.status)
      end
    end
  end
end
