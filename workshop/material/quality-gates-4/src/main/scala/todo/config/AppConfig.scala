package todo.config

import pureconfig.*

import java.nio.file.{Path, Paths}
import todo.OutputFormat

/** Typed application settings. Defaults match develop_app.v2 when nothing is configured. */
final case class AppConfig(
    store: String = "todos.yaml",
    format: String = "table",
    color: Boolean = true,
    assigner: Option[String] = None
) derives ConfigReader:
  def storePath: Path = Paths.get(store)

  def defaultFormat: Either[String, OutputFormat] =
    OutputFormat.parse(format, "todo.format")

object AppConfig:
  val defaults: AppConfig = AppConfig()

  /** Load from Typesafe Config/HOCON on the classpath (`application.conf` / `reference.conf`). */
  def load(): AppConfig =
    ConfigSource.default.at("todo").load[AppConfig].getOrElse(defaults)

  def loadFrom(source: ConfigSource): AppConfig =
    source.at("todo").load[AppConfig].getOrElse(defaults)

  /**
   * Resolve effective settings. Precedence: CLI overrides → env → file config → defaults.
   */
  def resolve(
      file: AppConfig,
      env: Map[String, String],
      cliStore: Option[String] = None,
      cliFormat: Option[String] = None,
      cliNoColor: Boolean = false
  ): AppConfig =
    val store = cliStore.orElse(env.get("TODO_STORE")).getOrElse(file.store)
    val format = cliFormat.orElse(env.get("TODO_FORMAT")).getOrElse(file.format)
    val color =
      if cliNoColor || env.contains("NO_COLOR") then false
      else file.color
    val assigner = env.get("TODO_ASSIGNER").orElse(file.assigner)
    AppConfig(store = store, format = format, color = color, assigner = assigner)
