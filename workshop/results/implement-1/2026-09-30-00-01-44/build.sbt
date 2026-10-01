ThisBuild / scalaVersion := "3.3.4"

ThisBuild / scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-unchecked",
  "-Werror"
)

lazy val root = (project in file("."))
  .settings(
    name := "todo-list-cli",
    libraryDependencies ++= Seq(
      "org.typelevel" %% "cats-core" % "2.12.0",
      "org.typelevel" %% "cats-effect" % "3.5.7",
      "org.scalameta" %% "munit" % "1.0.3" % Test,
      "org.typelevel" %% "munit-cats-effect" % "2.0.0" % Test,
      "org.scalameta" %% "munit-scalacheck" % "1.0.0" % Test
    )
  )
