# This file is responsible for configuring your application
# and its dependencies with the aid of the Mix.Config module.
#
# This configuration file is loaded before any dependency and
# is restricted to this project.

# General application configuration
use Mix.Config

# Configures the endpoint
config :collector, CollectorWeb.Endpoint,
  url: [host: "localhost"],
  secret_key_base: "+Y5gF0YOzk8niLls80Vhur6oCVK/ya5iZw+LhcT+x8FrE5Scy2smTJfE+tPWt0Pr",
  render_errors: [view: CollectorWeb.ErrorView, accepts: ~w(json), layout: false],
  pubsub_server: Collector.PubSub,
  live_view: [signing_salt: "0JYjOzVq"]

# Configures Elixir's Logger
config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

# Use Jason for JSON parsing in Phoenix
config :phoenix, :json_library, Jason

# Import environment specific config. This must remain at the bottom
# of this file so it overrides the configuration defined above.
import_config "#{Mix.env()}.exs"
