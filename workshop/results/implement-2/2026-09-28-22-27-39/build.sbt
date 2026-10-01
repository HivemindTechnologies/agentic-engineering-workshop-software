ThisBuild / scalaVersion := "3.3.4"
ThisBuild / version := "0.1.0-SNAPSHOT"
ThisBuild / organization := "hivemind"

lazy val root = (project in file("."))
  .settings(
    name := "todo-list-cli",
    Compile / run / fork := true,
    scalacOptions ++= Seq(
      "-deprecation",
      "-feature",
      "-unchecked",
      "-Werror"
    ),
    libraryDependencies ++= Seq(
      "org.typelevel" %% "cats-core" % "2.12.0",
      "org.typelevel" %% "cats-effect" % "3.5.7",
      "org.virtuslab" %% "scala-yaml" % "0.3.0",
      "org.scalameta" %% "munit" % "1.0.3" % Test,
      "org.typelevel" %% "munit-cats-effect" % "2.0.0" % Test,
      "org.scalameta" %% "munit-scalacheck" % "1.0.0" % Test
    ),
    testFrameworks += new TestFramework("munit.Framework")
  )
