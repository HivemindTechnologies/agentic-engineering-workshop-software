val scala3Version = "3.9.0"

lazy val root = project
  .in(file("."))
  .settings(
    name := "todo-list-cli",
    version := "0.1.0",
    scalaVersion := scala3Version,
    scalacOptions ++= Seq(
      "-deprecation",
      "-feature",
      "-unchecked",
      "-Werror"
    ),
    libraryDependencies ++= Seq(
      "org.typelevel" %% "cats-core" % "2.13.0",
      "org.typelevel" %% "cats-effect" % "3.7.1",
      "org.scalameta" %% "munit" % "1.3.6" % Test,
      "org.typelevel" %% "munit-cats-effect" % "2.2.1" % Test,
      "org.scalameta" %% "munit-scalacheck" % "1.3.1" % Test
    ),
    testFrameworks += new TestFramework("munit.Framework")
  )
