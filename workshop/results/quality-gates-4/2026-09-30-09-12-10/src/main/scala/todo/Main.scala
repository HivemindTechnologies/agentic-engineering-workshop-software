package todo

import cats.effect.{ExitCode, IO, IOApp}
import todo.config.AppConfig

object Main extends IOApp:
  def run(args: List[String]): IO[ExitCode] =
    val file = AppConfig.load()
    val cfg = AppConfig.resolve(file, sys.env.toMap)
    val tty = System.console() != null
    val color = cfg.color && tty
    val format = cfg.defaultFormat.getOrElse(OutputFormat.Table)
    Cli.run(args, cfg.storePath, System.out, color, format, cfg.assigner)
