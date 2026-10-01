package todo.config

import pureconfig.ConfigSource

class AppConfigSuite extends munit.FunSuite:
  test("defaults match develop_app.v2") {
    val c = AppConfig.defaults
    assertEquals(c.store, "todos.yaml")
    assertEquals(c.format, "table")
    assertEquals(c.color, true)
  }

  test("HOCON source overrides store and format") {
    val src = ConfigSource.string("""
      todo {
        store = "/tmp/t.yaml"
        format = "json"
        color = false
      }
      """)
    val c = AppConfig.loadFrom(src)
    assertEquals(c.store, "/tmp/t.yaml")
    assertEquals(c.format, "json")
    assertEquals(c.color, false)
  }

  test("env wins over file; CLI wins over env") {
    val file = AppConfig(store = "file.yaml", format = "table", color = true)
    val env = Map("TODO_STORE" -> "env.yaml", "TODO_FORMAT" -> "markdown")
    val fromEnv = AppConfig.resolve(file, env)
    assertEquals(fromEnv.store, "env.yaml")
    assertEquals(fromEnv.format, "markdown")
    val fromCli =
      AppConfig.resolve(file, env, cliStore = Some("cli.yaml"), cliFormat = Some("json"))
    assertEquals(fromCli.store, "cli.yaml")
    assertEquals(fromCli.format, "json")
  }

  test("NO_COLOR disables color") {
    val file = AppConfig.defaults
    val c = AppConfig.resolve(file, Map("NO_COLOR" -> "1"))
    assertEquals(c.color, false)
  }
