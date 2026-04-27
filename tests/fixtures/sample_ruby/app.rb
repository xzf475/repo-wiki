require "json"
require_relative "config"

# Handles HTTP request routing.
class Router
  # Creates a new Router instance.
  def initialize
    @routes = {}
  end

  # Registers a route with the given path and handler.
  def add_route(path, handler)
    @routes[path] = handler
  end

  # Dispatches the request to the matching handler.
  def dispatch(path)
    handler = @routes[path]
    handler.call if handler
  end
end

# Parses incoming HTTP requests.
module Parser
  # Parses a raw HTTP request string into a hash.
  def self.parse(raw)
    { body: raw.strip }
  end
end
