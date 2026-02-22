# frozen_string_literal: true

module Blackroad
  # Base error class for all BlackRoad errors
  class Error < StandardError
    attr_reader :code, :status_code

    def initialize(message, code: nil, status_code: nil)
      @code = code
      @status_code = status_code
      super(message)
    end
  end

  # Raised when authentication fails (invalid API key)
  class AuthenticationError < Error
    def initialize(message = "Invalid API key")
      super(message, code: "AUTHENTICATION_ERROR", status_code: 401)
    end
  end

  # Raised when a resource is not found
  class NotFoundError < Error
    attr_reader :resource

    def initialize(resource)
      @resource = resource
      super("Resource not found: #{resource}", code: "NOT_FOUND", status_code: 404)
    end
  end

  # Raised when rate limit is exceeded
  class RateLimitError < Error
    attr_reader :retry_after

    def initialize(retry_after = 1)
      @retry_after = retry_after
      super("Rate limit exceeded. Retry after #{retry_after} seconds", code: "RATE_LIMIT_EXCEEDED", status_code: 429)
    end
  end

  # Raised when request validation fails
  class ValidationError < Error
    attr_reader :details

    def initialize(details)
      @details = details
      super("Validation error: #{details}", code: "VALIDATION_ERROR", status_code: 422)
    end
  end

  # Raised when network/connection fails
  class ConnectionError < Error
    attr_reader :cause

    def initialize(message, cause: nil)
      @cause = cause
      super(message, code: "CONNECTION_ERROR")
    end
  end
end
